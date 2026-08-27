"""Typed, bounded, and user-friendly OpenAI integration."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeVar

import pandas as pd
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from utils.analytics import get_dataframe_summary
from utils.quality import generate_data_quality_report

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
MODEL_NAME = "gpt-4.1-mini"
MAX_PROMPT_CHARS = 20_000
MAX_QUESTION_CHARS = 2_000


class AIAnalyticsError(RuntimeError):
    """Base exception safe to display in the application."""


class AIServiceError(AIAnalyticsError):
    """The AI provider could not complete a request."""


class AIResponseError(AIAnalyticsError):
    """The provider returned an unusable structured response."""


class AnalystResponse(BaseModel):
    """Structured response for an open-ended analytics question."""

    model_config = ConfigDict(extra="forbid")
    answer: str = Field(min_length=1, max_length=4_000)


class ChartConfig(BaseModel):
    """Validated chart specification produced by the model."""

    model_config = ConfigDict(extra="forbid")
    chart_type: Literal["bar", "line", "histogram"]
    x_axis: str = Field(min_length=1)
    y_axis: str | None = None
    aggregation: Literal["sum", "average", "count", "none"] = "none"

    @model_validator(mode="after")
    def validate_chart_shape(self) -> ChartConfig:
        if self.chart_type == "histogram":
            if self.y_axis is not None or self.aggregation != "none":
                raise ValueError("histograms cannot use a y-axis or aggregation")
        elif self.y_axis is None:
            raise ValueError("bar and line charts require a y-axis")
        return self


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


def load_prompt(file_name: str) -> str:
    prompt_path = PROMPTS_DIR / file_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def _clean_question(question: str) -> str:
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("Enter a question before requesting AI analysis.")
    return cleaned[:MAX_QUESTION_CHARS]


def _bounded_prompt(prompt: str) -> str:
    if len(prompt) <= MAX_PROMPT_CHARS:
        return prompt
    return prompt[:MAX_PROMPT_CHARS] + "\n[Dataset context truncated for safety.]"


def _request_structured_response(
    client: OpenAI,
    *,
    prompt: str,
    response_model: type[ResponseModel],
) -> ResponseModel:
    try:
        response = client.responses.parse(
            model=MODEL_NAME,
            input=_bounded_prompt(prompt),
            text_format=response_model,
        )
    except OpenAIError as exc:
        raise AIServiceError(
            "AI analysis is temporarily unavailable. Please retry or continue in local mode."
        ) from exc

    parsed = response.output_parsed
    if parsed is None:
        raise AIResponseError("The AI response could not be validated. Try rephrasing the request.")
    if isinstance(parsed, response_model):
        return parsed
    try:
        return response_model.model_validate(parsed)
    except ValidationError as exc:
        raise AIResponseError(
            "The AI response did not match the required format. Try rephrasing the request."
        ) from exc


def ask_ai(question: str, df: pd.DataFrame, client: OpenAI) -> str:
    """Answer a data question through a typed provider response."""
    prompt = load_prompt("analyst_prompt.txt").format(
        summary=get_dataframe_summary(df),
        quality_report="\n".join(generate_data_quality_report(df)),
        question=_clean_question(question),
    )
    return _request_structured_response(
        client,
        prompt=prompt,
        response_model=AnalystResponse,
    ).answer


def generate_chart_config(question: str, df: pd.DataFrame, client: OpenAI) -> dict:
    """Generate and validate a chart specification against the active dataset."""
    prompt = load_prompt("chart_prompt.txt").format(
        columns=list(df.columns),
        question=_clean_question(question),
    )
    config = _request_structured_response(
        client,
        prompt=prompt,
        response_model=ChartConfig,
    )
    required_columns = {config.x_axis}
    if config.y_axis is not None:
        required_columns.add(config.y_axis)
    unknown_columns = sorted(required_columns.difference(df.columns))
    if unknown_columns:
        raise AIResponseError(
            f"The AI selected unavailable columns: {', '.join(unknown_columns)}."
        )
    return config.model_dump()

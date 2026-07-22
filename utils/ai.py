import json
from pathlib import Path

import pandas as pd
from openai import OpenAI

from utils.analytics import get_dataframe_summary
from utils.quality import generate_data_quality_report


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def load_prompt(file_name: str) -> str:
    prompt_path = PROMPTS_DIR / file_name

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def ask_ai(question: str, df: pd.DataFrame, client: OpenAI) -> str:
    summary = get_dataframe_summary(df)
    quality_report = generate_data_quality_report(df)
    prompt_template = load_prompt("analyst_prompt.txt")

    prompt = prompt_template.format(
        summary=summary,
        quality_report="\n".join(quality_report),
        question=question
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def generate_chart_config(
    question: str,
    df: pd.DataFrame,
    client: OpenAI
) -> dict | None:
    prompt_template = load_prompt("chart_prompt.txt")

    prompt = prompt_template.format(
        columns=list(df.columns),
        question=question
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        result = json.loads(response.output_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(result, dict):
        return None

    return result
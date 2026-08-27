from types import SimpleNamespace

import pandas as pd
import pytest

from utils.ai import (
    MAX_PROMPT_CHARS,
    AIResponseError,
    AnalystResponse,
    ChartConfig,
    ask_ai,
    generate_chart_config,
)


class FakeResponses:
    def __init__(self, output_parsed):
        self.output_parsed = output_parsed
        self.request = None

    def parse(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_parsed=self.output_parsed)


def fake_client(output_parsed):
    responses = FakeResponses(output_parsed)
    return SimpleNamespace(responses=responses), responses


def sample_dataframe():
    return pd.DataFrame(
        {"campaign": ["Search", "Social"], "revenue": [250.0, 80.0]}
    )


def test_ask_ai_uses_typed_bounded_response():
    client, responses = fake_client(AnalystResponse(answer="Search leads revenue."))

    answer = ask_ai("Which campaign leads?", sample_dataframe(), client)

    assert answer == "Search leads revenue."
    assert responses.request["text_format"] is AnalystResponse
    assert len(responses.request["input"]) <= MAX_PROMPT_CHARS + 41


def test_chart_config_is_schema_validated_and_serialized():
    parsed = ChartConfig(
        chart_type="bar",
        x_axis="campaign",
        y_axis="revenue",
        aggregation="sum",
    )
    client, responses = fake_client(parsed)

    config = generate_chart_config("Revenue by campaign", sample_dataframe(), client)

    assert config == {
        "chart_type": "bar",
        "x_axis": "campaign",
        "y_axis": "revenue",
        "aggregation": "sum",
    }
    assert responses.request["text_format"] is ChartConfig


def test_chart_config_rejects_hallucinated_columns():
    client, _ = fake_client(
        ChartConfig(
            chart_type="bar",
            x_axis="region",
            y_axis="revenue",
            aggregation="sum",
        )
    )

    with pytest.raises(AIResponseError, match="region"):
        generate_chart_config("Revenue by region", sample_dataframe(), client)


def test_missing_structured_output_has_friendly_error():
    client, _ = fake_client(None)

    with pytest.raises(AIResponseError, match="could not be validated"):
        ask_ai("Summarize", sample_dataframe(), client)


def test_chart_schema_enforces_histogram_shape():
    with pytest.raises(ValueError, match="histograms"):
        ChartConfig(
            chart_type="histogram",
            x_axis="revenue",
            y_axis="campaign",
            aggregation="sum",
        )

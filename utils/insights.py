"""Deterministic insight recommendations for uploaded analytics datasets."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class InsightRecommendation:
    """A recruiter-friendly, UI-safe recommendation generated from data signals."""

    title: str
    severity: str
    detail: str
    recommendation: str

    def as_markdown(self) -> str:
        """Render the insight as compact markdown for Streamlit."""
        return (
            f"**{self.title}**  \n"
            f"Severity: `{self.severity}`  \n"
            f"{self.detail}  \n"
            f"Recommendation: {self.recommendation}"
        )


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")


def _find_column(columns: Iterable[str], keywords: tuple[str, ...]) -> str | None:
    normalized = {column: _normalize(column) for column in columns}
    for column, clean_name in normalized.items():
        if any(keyword in clean_name for keyword in keywords):
            return column
    return None


def _format_number(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    if abs(float(value)) >= 1000:
        return f"{float(value):,.0f}"
    return f"{float(value):,.2f}".rstrip("0").rstrip(".")


def _missing_value_insights(df: pd.DataFrame) -> list[InsightRecommendation]:
    if df.empty:
        return []

    missing_rates = (df.isna().mean() * 100).sort_values(ascending=False)
    flagged = missing_rates[missing_rates >= 10]
    insights: list[InsightRecommendation] = []

    for column, rate in flagged.head(3).items():
        severity = "high" if rate >= 30 else "medium"
        insights.append(
            InsightRecommendation(
                title=f"Missing data detected in {column}",
                severity=severity,
                detail=f"{column} has {_format_number(rate)}% missing values.",
                recommendation=(
                    "Validate the upstream source and decide whether to impute, exclude, "
                    "or route incomplete records into a quality review workflow."
                ),
            )
        )

    return insights


def _duplicate_insight(df: pd.DataFrame) -> list[InsightRecommendation]:
    duplicate_count = int(df.duplicated().sum())
    if duplicate_count == 0 or df.empty:
        return []

    duplicate_rate = duplicate_count / len(df) * 100
    severity = "high" if duplicate_rate >= 5 else "medium"
    return [
        InsightRecommendation(
            title="Duplicate records may affect metrics",
            severity=severity,
            detail=(
                f"Found {duplicate_count:,} duplicate rows "
                f"({_format_number(duplicate_rate)}% of the dataset)."
            ),
            recommendation=(
                "Confirm the business grain of the dataset and deduplicate before calculating "
                "KPIs such as revenue, orders, spend, or conversions."
            ),
        )
    ]


def _roas_insight(df: pd.DataFrame) -> list[InsightRecommendation]:
    revenue_col = _find_column(df.columns, ("revenue", "sales", "amount"))
    spend_col = _find_column(df.columns, ("spend", "cost", "expense"))
    category_col = _find_column(
        df.columns,
        ("campaign", "channel", "platform", "source", "category", "segment"),
    )

    if not revenue_col or not spend_col or not category_col:
        return []
    if not pd.api.types.is_numeric_dtype(df[revenue_col]) or not pd.api.types.is_numeric_dtype(df[spend_col]):
        return []

    grouped = df.groupby(category_col, dropna=False)[[revenue_col, spend_col]].sum()
    grouped = grouped[grouped[spend_col] > 0].copy()
    if grouped.empty:
        return []

    grouped["roas"] = grouped[revenue_col] / grouped[spend_col]
    low_roas = grouped.sort_values("roas").head(1)
    group_name = str(low_roas.index[0])
    roas = float(low_roas["roas"].iloc[0])
    spend = float(low_roas[spend_col].iloc[0])

    if roas >= 2:
        return []

    severity = "high" if roas < 1 else "medium"
    return [
        InsightRecommendation(
            title="Low return segment found",
            severity=severity,
            detail=(
                f"{category_col} '{group_name}' has ROAS of {_format_number(roas)} "
                f"on {_format_number(spend)} total {spend_col}."
            ),
            recommendation=(
                "Review budget allocation, targeting, and creative performance for this segment "
                "before increasing spend."
            ),
        )
    ]


def _concentration_insight(df: pd.DataFrame) -> list[InsightRecommendation]:
    metric_col = _find_column(df.columns, ("revenue", "sales", "amount", "spend", "cost"))
    category_col = _find_column(
        df.columns,
        ("campaign", "channel", "platform", "source", "category", "segment", "product"),
    )

    if not metric_col or not category_col or not pd.api.types.is_numeric_dtype(df[metric_col]):
        return []

    grouped = df.groupby(category_col, dropna=False)[metric_col].sum().sort_values(ascending=False)
    total = grouped.sum()
    if total <= 0 or grouped.empty:
        return []

    top_name = str(grouped.index[0])
    top_share = float(grouped.iloc[0] / total * 100)
    if top_share < 40:
        return []

    severity = "high" if top_share >= 60 else "medium"
    return [
        InsightRecommendation(
            title="Metric concentration risk",
            severity=severity,
            detail=f"'{top_name}' contributes {_format_number(top_share)}% of total {metric_col}.",
            recommendation=(
                "Check whether performance depends too heavily on one segment and compare the "
                "next-best segments for diversification opportunities."
            ),
        )
    ]


def generate_insight_recommendations(df: pd.DataFrame, limit: int = 5) -> list[InsightRecommendation]:
    """Generate deterministic business and data-quality recommendations.

    The function intentionally avoids LLM calls so the public demo remains useful without an
    API key and test results stay reproducible.
    """
    if df.empty:
        return [
            InsightRecommendation(
                title="Dataset is empty",
                severity="high",
                detail="No rows are available for analysis.",
                recommendation="Upload a non-empty CSV file before generating insights.",
            )
        ]

    insights: list[InsightRecommendation] = []
    insights.extend(_duplicate_insight(df))
    insights.extend(_missing_value_insights(df))
    insights.extend(_roas_insight(df))
    insights.extend(_concentration_insight(df))

    if not insights:
        insights.append(
            InsightRecommendation(
                title="No major automated risk detected",
                severity="low",
                detail="The deterministic checks did not find major duplicate, missing-value, ROAS, or concentration issues.",
                recommendation="Continue with deeper trend, cohort, and segment-level analysis.",
            )
        )

    return insights[:limit]

"""Deterministic natural-language analytics that do not require an API key."""

from __future__ import annotations

import re

import pandas as pd


def _display_name(column: str) -> str:
    return str(column).replace("_", " ")


def _format_number(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{float(value):,.2f}"


def _mentioned_columns(question: str, df: pd.DataFrame) -> list[str]:
    normalized_question = re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()
    matches = []
    for column in sorted(df.columns, key=lambda item: len(str(item)), reverse=True):
        normalized_column = re.sub(r"[^a-z0-9]+", " ", str(column).lower()).strip()
        if normalized_column and re.search(rf"\b{re.escape(normalized_column)}\b", normalized_question):
            matches.append(column)
    return matches


def _summary_answer(df: pd.DataFrame) -> str:
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(exclude="number").columns.tolist()
    return (
        "### Dataset summary\n"
        f"- **Rows:** {len(df):,}\n"
        f"- **Columns:** {len(df.columns):,}\n"
        f"- **Numeric columns:** {', '.join(map(_display_name, numeric)) or 'None'}\n"
        f"- **Other columns:** {', '.join(map(_display_name, categorical)) or 'None'}\n"
        f"- **Missing cells:** {int(df.isna().sum().sum()):,}\n"
        f"- **Duplicate rows:** {int(df.duplicated().sum()):,}"
    )


def _quality_answer(df: pd.DataFrame) -> str:
    missing = df.isna().sum().sort_values(ascending=False)
    affected = missing[missing > 0]
    details = (
        "\n".join(f"- **{_display_name(column)}:** {int(count):,}" for column, count in affected.items())
        if not affected.empty
        else "- No missing values detected."
    )
    return (
        "### Data quality\n"
        f"- **Missing cells:** {int(missing.sum()):,}\n"
        f"- **Duplicate rows:** {int(df.duplicated().sum()):,}\n"
        f"- **Completely empty columns:** {int(df.isna().all().sum()):,}\n\n"
        f"Missing values by column:\n{details}"
    )


def _correlation_answer(df: pd.DataFrame) -> str:
    numeric = df.select_dtypes(include="number")
    if len(numeric.columns) < 2:
        return "Correlation analysis requires at least two numeric columns."
    correlations = numeric.corr()
    candidates = []
    for index, left in enumerate(correlations.columns):
        for right in correlations.columns[index + 1 :]:
            value = correlations.loc[left, right]
            if pd.notna(value):
                candidates.append((abs(value), value, left, right))
    if not candidates:
        return "No usable numeric correlation could be calculated."
    _, value, left, right = max(candidates)
    return (
        "### Strongest numeric correlation\n"
        f"**{_display_name(left)}** and **{_display_name(right)}**: `{value:.3f}`\n\n"
        "Correlation describes association, not causation."
    )


def _grouped_answer(question: str, df: pd.DataFrame, columns: list[str]) -> str | None:
    numeric = [column for column in columns if pd.api.types.is_numeric_dtype(df[column])]
    categories = [column for column in columns if column not in numeric]
    if not numeric or not categories or " by " not in f" {question.lower()} ":
        return None

    metric, category = numeric[0], categories[0]
    lowered = question.lower()
    if "average" in lowered or "mean" in lowered:
        aggregation, label = "mean", "average"
    elif "count" in lowered:
        aggregation, label = "count", "count"
    elif "minimum" in lowered or " min " in f" {lowered} ":
        aggregation, label = "min", "minimum"
    elif "maximum" in lowered or " max " in f" {lowered} ":
        aggregation, label = "max", "maximum"
    else:
        aggregation, label = "sum", "total"

    result = (
        df.groupby(category, dropna=False)[metric]
        .agg(aggregation)
        .sort_values(ascending=False)
        .head(5)
    )
    rows = "\n".join(
        f"{rank}. **{group}:** {_format_number(value)}"
        for rank, (group, value) in enumerate(result.items(), start=1)
    )
    return (
        f"### Top {_display_name(category)} by {label} {_display_name(metric)}\n{rows}"
    )


def answer_locally(question: str, df: pd.DataFrame) -> str:
    """Answer common analytical questions with deterministic Pandas operations."""
    cleaned_question = question.strip()
    if not cleaned_question:
        return "Enter a question about the uploaded dataset."

    lowered = cleaned_question.lower()
    columns = _mentioned_columns(cleaned_question, df)

    if any(term in lowered for term in ("summary", "summarize", "overview", "describe dataset")):
        return _summary_answer(df)
    if any(term in lowered for term in ("missing", "null", "quality", "duplicate")):
        return _quality_answer(df)
    if "correlation" in lowered or "correlate" in lowered:
        return _correlation_answer(df)

    grouped = _grouped_answer(cleaned_question, df, columns)
    if grouped:
        return grouped

    numeric = [column for column in columns if pd.api.types.is_numeric_dtype(df[column])]
    if numeric:
        column = numeric[0]
        series = df[column].dropna()
        if "total" in lowered or "sum" in lowered:
            operation, value = "Total", series.sum()
        elif "average" in lowered or "mean" in lowered:
            operation, value = "Average", series.mean()
        elif "minimum" in lowered or " min " in f" {lowered} ":
            operation, value = "Minimum", series.min()
        elif "maximum" in lowered or " max " in f" {lowered} ":
            operation, value = "Maximum", series.max()
        else:
            operation = "Summary"
            return (
                f"### {_display_name(column)} summary\n"
                f"- **Count:** {int(series.count()):,}\n"
                f"- **Average:** {_format_number(series.mean())}\n"
                f"- **Minimum:** {_format_number(series.min())}\n"
                f"- **Maximum:** {_format_number(series.max())}"
            )
        return f"### {operation}\n**{_display_name(column)}:** {_format_number(value)}"

    return (
        "I can answer local questions about dataset summaries, missing values, duplicates, "
        "correlations, numeric totals or averages, and requests like **top campaign by revenue**."
    )

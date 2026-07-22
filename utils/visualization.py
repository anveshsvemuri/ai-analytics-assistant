import pandas as pd
import matplotlib.pyplot as plt


def create_basic_chart(df: pd.DataFrame, chart_type: str, selected_column: str):
    fig, ax = plt.subplots()

    if chart_type == "Bar Chart":
        df[selected_column].plot(kind="bar", ax=ax)
        ax.set_xlabel("Row Number")
        ax.set_ylabel(selected_column)

    elif chart_type == "Line Chart":
        df[selected_column].plot(kind="line", ax=ax)
        ax.set_xlabel("Row Number")
        ax.set_ylabel(selected_column)

    elif chart_type == "Histogram":
        df[selected_column].plot(kind="hist", ax=ax)
        ax.set_xlabel(selected_column)

    ax.set_title(f"{chart_type} of {selected_column}")

    return fig


def create_correlation_chart(correlation: pd.DataFrame):
    fig, ax = plt.subplots()
    cax = ax.matshow(correlation)
    fig.colorbar(cax)

    ax.set_xticks(range(len(correlation.columns)))
    ax.set_yticks(range(len(correlation.columns)))
    ax.set_xticklabels(correlation.columns, rotation=90)
    ax.set_yticklabels(correlation.columns)

    return fig


def create_ai_chart(chart_config: dict, df: pd.DataFrame):
    chart_type = chart_config.get("chart_type")
    x_axis = chart_config.get("x_axis")
    y_axis = chart_config.get("y_axis")
    aggregation = chart_config.get("aggregation")

    if chart_type not in ["bar", "line", "histogram"]:
        return None, "Unsupported chart type."

    if x_axis not in df.columns:
        return None, f"Column '{x_axis}' does not exist in the dataset."

    if chart_type != "histogram" and y_axis not in df.columns:
        return None, f"Column '{y_axis}' does not exist in the dataset."
    supported_aggregations = {"sum", "average", "count", "none"}

    if aggregation not in supported_aggregations:
        return None, f"Unsupported aggregation: {aggregation}"

    if chart_type in {"bar", "line"}:
        if not pd.api.types.is_numeric_dtype(df[y_axis]):
            return None, (
                f"'{y_axis}' must be a numeric column for a {chart_type} chart."
            )
    fig, ax = plt.subplots()

    if chart_type == "histogram":
        if not pd.api.types.is_numeric_dtype(df[x_axis]):
            return None, f"Histogram requires a numeric column, but '{x_axis}' is not numeric."

        df[x_axis].plot(kind="hist", ax=ax)
        ax.set_title(f"Distribution of {x_axis}")
        ax.set_xlabel(x_axis)

    elif chart_type == "bar":
        if aggregation == "sum":
            chart_data = df.groupby(x_axis)[y_axis].sum().sort_values(ascending=False).head(10)
        elif aggregation == "average":
            chart_data = df.groupby(x_axis)[y_axis].mean().sort_values(ascending=False).head(10)
        elif aggregation == "count":
            chart_data = df.groupby(x_axis)[y_axis].count().sort_values(ascending=False).head(10)
        else:
            chart_data = df.set_index(x_axis)[y_axis].head(10)

        chart_data.plot(kind="bar", ax=ax)
        ax.set_title(f"{y_axis} by {x_axis}")
        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)

    elif chart_type == "line":
        chart_data = df[[x_axis, y_axis]].dropna()
        chart_data.plot(x=x_axis, y=y_axis, kind="line", ax=ax)
        ax.set_title(f"{y_axis} over {x_axis}")
        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)

    return fig, None

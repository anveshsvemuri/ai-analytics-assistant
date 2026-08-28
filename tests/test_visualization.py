import matplotlib.pyplot as plt
import pandas as pd
import pytest

from utils.visualization import (
    create_ai_chart,
    create_basic_chart,
    create_correlation_chart,
)


@pytest.fixture
def frame():
    return pd.DataFrame(
        {
            "campaign": ["Search", "Social", "Search"],
            "revenue": [250.0, 80.0, 150.0],
            "clicks": [25, 12, 18],
        }
    )


@pytest.mark.parametrize("chart_type", ["Bar Chart", "Line Chart", "Histogram"])
def test_basic_chart_renders_numeric_series(frame, chart_type):
    figure = create_basic_chart(frame, chart_type, "revenue")

    assert figure.axes[0].get_title() == f"{chart_type} of revenue"
    plt.close(figure)


def test_basic_chart_rejects_unknown_types_and_non_numeric_columns(frame):
    with pytest.raises(ValueError, match="Unsupported chart type"):
        create_basic_chart(frame, "Pie Chart", "revenue")
    with pytest.raises(ValueError, match="must be a numeric column"):
        create_basic_chart(frame, "Bar Chart", "campaign")


def test_ai_bar_chart_aggregates_and_sorts_top_categories(frame):
    figure, error = create_ai_chart(
        {
            "chart_type": "bar",
            "x_axis": "campaign",
            "y_axis": "revenue",
            "aggregation": "sum",
        },
        frame,
    )

    assert error is None
    labels = [label.get_text() for label in figure.axes[0].get_xticklabels()]
    assert labels == ["Search", "Social"]
    plt.close(figure)


def test_ai_chart_returns_actionable_validation_errors(frame):
    _, missing_error = create_ai_chart(
        {"chart_type": "bar", "x_axis": "region", "y_axis": "revenue", "aggregation": "sum"},
        frame,
    )
    _, type_error = create_ai_chart(
        {
            "chart_type": "histogram",
            "x_axis": "campaign",
            "y_axis": None,
            "aggregation": "none",
        },
        frame,
    )

    assert missing_error == "Column 'region' does not exist in the dataset."
    assert type_error == "Histogram requires a numeric column, but 'campaign' is not numeric."


def test_correlation_chart_requires_matrix_and_labels_axes(frame):
    correlation = frame[["revenue", "clicks"]].corr()
    figure = create_correlation_chart(correlation)

    assert [label.get_text() for label in figure.axes[0].get_xticklabels()] == [
        "revenue",
        "clicks",
    ]
    plt.close(figure)
    with pytest.raises(ValueError, match="empty"):
        create_correlation_chart(pd.DataFrame())

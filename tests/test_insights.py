import pandas as pd

from utils.insights import generate_insight_recommendations


def test_empty_dataset_returns_high_severity_recommendation():
    insights = generate_insight_recommendations(pd.DataFrame())

    assert len(insights) == 1
    assert insights[0].severity == "high"
    assert "empty" in insights[0].title.lower()


def test_duplicate_rows_generate_recommendation():
    df = pd.DataFrame(
        {
            "campaign": ["Search", "Search", "Search"],
            "revenue": [100, 100, 50],
            "spend": [80, 80, 25],
        }
    )

    titles = [insight.title for insight in generate_insight_recommendations(df)]

    assert "Duplicate records may affect metrics" in titles


def test_missing_values_generate_column_specific_recommendation():
    df = pd.DataFrame(
        {
            "campaign": ["Search", "Social", "Display", "Video"],
            "revenue": [100, None, None, None],
            "spend": [80, 50, 40, 20],
        }
    )

    insights = generate_insight_recommendations(df)

    assert any("revenue" in insight.title for insight in insights)
    assert any(insight.severity in {"medium", "high"} for insight in insights)


def test_low_roas_segment_is_flagged():
    df = pd.DataFrame(
        {
            "campaign": ["Search", "Social", "Display"],
            "revenue": [500, 50, 400],
            "spend": [100, 100, 100],
        }
    )

    insights = generate_insight_recommendations(df)

    assert any(insight.title == "Low return segment found" for insight in insights)
    assert any("Social" in insight.detail for insight in insights)


def test_no_major_risks_returns_low_severity_fallback():
    df = pd.DataFrame(
        {
            "campaign": ["Search", "Social", "Display"],
            "revenue": [300, 280, 260],
            "spend": [100, 100, 100],
        }
    )

    insights = generate_insight_recommendations(df)

    assert len(insights) == 1
    assert insights[0].severity == "low"

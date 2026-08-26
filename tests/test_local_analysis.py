import pandas as pd

from utils.local_analysis import answer_locally


def sample_dataframe():
    return pd.DataFrame(
        {
            "campaign": ["Search", "Search", "Social"],
            "revenue": [100.0, 150.0, 80.0],
            "spend": [50.0, 75.0, 60.0],
            "note": ["A", None, "C"],
        }
    )


def test_summary_reports_shape_and_quality_counts():
    answer = answer_locally("Summarize this dataset", sample_dataframe())

    assert "Rows:** 3" in answer
    assert "Columns:** 4" in answer
    assert "Missing cells:** 1" in answer


def test_quality_answer_identifies_missing_column():
    answer = answer_locally("What data quality issues are there?", sample_dataframe())

    assert "note:** 1" in answer
    assert "Duplicate rows:** 0" in answer


def test_numeric_aggregation_uses_mentioned_column():
    answer = answer_locally("What is the total revenue?", sample_dataframe())

    assert "revenue:** 330" in answer


def test_grouped_ranking_is_deterministic():
    answer = answer_locally("Show top campaign by revenue", sample_dataframe())

    assert "Search:** 250" in answer
    assert answer.index("Search") < answer.index("Social")


def test_correlation_reports_the_strongest_pair():
    answer = answer_locally("Show the strongest correlation", sample_dataframe())

    assert "revenue" in answer
    assert "spend" in answer
    assert "Correlation describes association" in answer

import pandas as pd


def calculate_health_score(df: pd.DataFrame) -> tuple[int, dict]:
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    missing_percentage = (missing_cells / total_cells) * 100 if total_cells > 0 else 0

    duplicate_rows = df.duplicated().sum()
    duplicate_percentage = (duplicate_rows / len(df)) * 100 if len(df) > 0 else 0

    empty_columns = df.columns[df.isnull().all()].tolist()

    score = 100
    score -= min(missing_percentage, 40)
    score -= min(duplicate_percentage, 30)
    score -= len(empty_columns) * 10
    score = max(0, int(score))

    details = {
        "missing_percentage": round(missing_percentage, 2),
        "duplicate_rows": int(duplicate_rows),
        "duplicate_percentage": round(duplicate_percentage, 2),
        "empty_columns": empty_columns
    }

    return score, details


def generate_data_quality_report(df: pd.DataFrame) -> list:
    recommendations = []

    missing = df.isnull().sum()

    for col, count in missing.items():
        if count > 0:
            recommendations.append(f"'{col}' has {count} missing values.")

    duplicates = df.duplicated().sum()

    if duplicates > 0:
        recommendations.append(f"The dataset contains {duplicates} duplicate rows.")

    numeric_columns = df.select_dtypes(include="number").columns

    for col in numeric_columns:
        if (df[col] < 0).any():
            recommendations.append(f"'{col}' contains negative values.")

    object_columns = df.select_dtypes(include="object").columns

    for col in object_columns:
        unique = df[col].nunique()

        if unique > len(df) * 0.8:
            recommendations.append(f"'{col}' has very high cardinality.")

        try:
            pd.to_datetime(df[col], errors="raise")
            recommendations.append(f"'{col}' appears to be a date column.")
        except Exception:
            pass

    if not recommendations:
        recommendations.append("No major data quality issues detected.")

    return recommendations
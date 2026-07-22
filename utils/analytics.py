import pandas as pd


def get_dataframe_summary(df: pd.DataFrame) -> str:
    numeric_summary = "No numeric columns found."

    if not df.select_dtypes(include="number").empty:
        numeric_summary = df.describe().to_string()

    categorical_summary = ""
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns

    for col in categorical_columns:
        top_values = df[col].value_counts().head(5).to_string()
        categorical_summary += f"""
Column: {col}
Unique Values: {df[col].nunique()}
Top Values:
{top_values}
"""

    summary = f"""
Dataset Summary:
Rows: {df.shape[0]}
Columns: {df.shape[1]}

Column Names:
{list(df.columns)}

Data Types:
{df.dtypes.to_string()}

Missing Values:
{df.isnull().sum().to_string()}

Duplicate Rows:
{df.duplicated().sum()}

Numeric Statistics:
{numeric_summary}

Categorical Summary:
{categorical_summary}

First 10 Rows:
{df.head(10).to_string()}
"""
    return summary


def get_column_info(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isnull().sum().values,
        "Missing %": (df.isnull().mean() * 100).round(2).values,
        "Unique Values": df.nunique().values
    })


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()

def get_category_columns(df: pd.DataFrame) -> list:
    return df.select_dtypes(include=["object", "category", "string"]).columns.tolist()


def perform_group_analysis(
    df: pd.DataFrame,
    category_col: str,
    metric_col: str,
    aggregation: str
) -> pd.DataFrame:
    if aggregation == "sum":
        result = df.groupby(category_col)[metric_col].sum()
    elif aggregation == "average":
        result = df.groupby(category_col)[metric_col].mean()
    elif aggregation == "count":
        result = df.groupby(category_col)[metric_col].count()
    elif aggregation == "min":
        result = df.groupby(category_col)[metric_col].min()
    elif aggregation == "max":
        result = df.groupby(category_col)[metric_col].max()
    else:
        raise ValueError("Invalid aggregation selected.")

    return result.sort_values(ascending=False).reset_index()
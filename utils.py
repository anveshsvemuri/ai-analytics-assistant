import pandas as pd


def get_dataframe_summary(df: pd.DataFrame) -> str:
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

First 5 Rows:
{df.head().to_string()}
"""
    return summary


def get_column_info(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isnull().sum().values,
        "Missing %": (df.isnull().mean() * 100).round(2).values
    })


def get_numeric_columns(df: pd.DataFrame) -> list:
    return df.select_dtypes(include=["int64", "float64"]).columns.tolist()


def get_category_columns(df: pd.DataFrame) -> list:
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


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
        raise ValueError("Invalid aggregation selected")

    return result.sort_values(ascending=False).reset_index()


def get_csv_download(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8")
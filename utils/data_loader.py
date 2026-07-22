import pandas as pd


def load_csv(uploaded_file) -> pd.DataFrame:
    """Read and validate an uploaded CSV file."""

    if uploaded_file is None:
        raise ValueError("No CSV file was uploaded.")

    try:
        df = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV file contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The uploaded file is not a valid CSV.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(
            "The CSV encoding could not be read. Save it as UTF-8 and upload it again."
        ) from exc

    if df.empty:
        raise ValueError("The uploaded CSV file is empty.")

    if len(df.columns) == 0:
        raise ValueError("The uploaded CSV does not contain any columns.")

    return df
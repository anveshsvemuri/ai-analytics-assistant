"""Safe, predictable CSV ingestion for the Streamlit application."""

from __future__ import annotations

from typing import BinaryIO

import pandas as pd

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_ROWS = 200_000
MAX_COLUMNS = 200


def _stream_size(uploaded_file: BinaryIO) -> int | None:
    """Return stream size without changing the caller's read position."""
    if hasattr(uploaded_file, "size"):
        return int(uploaded_file.size)

    if not all(hasattr(uploaded_file, method) for method in ("seek", "tell")):
        return None

    current_position = uploaded_file.tell()
    uploaded_file.seek(0, 2)
    size = uploaded_file.tell()
    uploaded_file.seek(current_position)
    return size


def load_csv(uploaded_file: BinaryIO) -> pd.DataFrame:
    """Read a CSV after enforcing upload, shape, and schema guardrails."""
    if uploaded_file is None:
        raise ValueError("No CSV file was uploaded.")

    size = _stream_size(uploaded_file)
    if size is not None and size > MAX_UPLOAD_BYTES:
        raise ValueError("The CSV exceeds the 25 MB upload limit.")

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    try:
        dataframe = pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The uploaded CSV file contains no data.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError("The uploaded file is not a valid CSV.") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(
            "The CSV encoding could not be read. Save it as UTF-8 and upload it again."
        ) from exc

    if dataframe.empty:
        raise ValueError("The uploaded CSV file is empty.")
    if len(dataframe.columns) == 0:
        raise ValueError("The uploaded CSV does not contain any columns.")
    if len(dataframe) > MAX_ROWS:
        raise ValueError(f"The CSV exceeds the {MAX_ROWS:,}-row analysis limit.")
    if len(dataframe.columns) > MAX_COLUMNS:
        raise ValueError(f"The CSV exceeds the {MAX_COLUMNS}-column analysis limit.")

    blank_columns = [column for column in dataframe.columns if not str(column).strip()]
    if blank_columns:
        raise ValueError("The CSV contains one or more blank column names.")

    return dataframe

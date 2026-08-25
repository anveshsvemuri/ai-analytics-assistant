from io import BytesIO

import pandas as pd
import pytest

from utils import data_loader


def csv_stream(content: str) -> BytesIO:
    return BytesIO(content.encode("utf-8"))


def test_load_csv_returns_dataframe_and_rewinds_stream():
    stream = csv_stream("campaign,spend\nSearch,100\nSocial,75\n")
    stream.read(4)

    result = data_loader.load_csv(stream)

    expected = pd.DataFrame({"campaign": ["Search", "Social"], "spend": [100, 75]})
    pd.testing.assert_frame_equal(result, expected)


def test_load_csv_rejects_missing_and_empty_inputs():
    with pytest.raises(ValueError, match="No CSV"):
        data_loader.load_csv(None)
    with pytest.raises(ValueError, match="contains no data"):
        data_loader.load_csv(csv_stream(""))


def test_load_csv_rejects_upload_over_size_limit(monkeypatch):
    stream = csv_stream("value\n1\n")
    monkeypatch.setattr(data_loader, "MAX_UPLOAD_BYTES", 2)

    with pytest.raises(ValueError, match="25 MB upload limit"):
        data_loader.load_csv(stream)


def test_load_csv_rejects_excessive_rows(monkeypatch):
    monkeypatch.setattr(data_loader, "MAX_ROWS", 1)

    with pytest.raises(ValueError, match="1-row analysis limit"):
        data_loader.load_csv(csv_stream("value\n1\n2\n"))


def test_load_csv_rejects_excessive_columns(monkeypatch):
    monkeypatch.setattr(data_loader, "MAX_COLUMNS", 2)

    with pytest.raises(ValueError, match="2-column analysis limit"):
        data_loader.load_csv(csv_stream("a,b,c\n1,2,3\n"))

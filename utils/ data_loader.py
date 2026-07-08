import pandas as pd


def load_csv(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file)

    if df.empty:
        raise ValueError("The uploaded CSV file is empty.")

    return df
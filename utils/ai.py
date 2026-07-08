import json
import pandas as pd
from openai import OpenAI

from utils.analytics import get_dataframe_summary
from utils.quality import generate_data_quality_report


def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def ask_ai(question: str, df: pd.DataFrame, client: OpenAI) -> str:
    summary = get_dataframe_summary(df)
    quality_report = generate_data_quality_report(df)
    prompt_template = load_prompt("prompts/analyst_prompt.txt")

    prompt = prompt_template.format(
        summary=summary,
        quality_report=quality_report,
        question=question
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def generate_chart_config(question: str, df: pd.DataFrame, client: OpenAI):
    columns = list(df.columns)
    prompt_template = load_prompt("prompts/chart_prompt.txt")

    prompt = prompt_template.format(
        columns=columns,
        question=question
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError:
        return None
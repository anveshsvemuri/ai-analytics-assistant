# AI Analytics Assistant

A Streamlit application that helps business users profile CSV datasets, investigate data quality, run grouped analysis, build charts, and ask natural-language questions—with or without an OpenAI API key.

## What it demonstrates

- Modular Python analytics and visualization utilities
- CSV validation with upload and dataset-shape guardrails
- Automated profiling, health scoring, and quality recommendations
- Deterministic grouped analysis, chart generation, and natural-language answers
- Prompt-driven dataset explanations and chart configuration
- Schema-validated AI answers and chart specifications
- Bounded AI prompts with provider retry, timeout, and friendly error handling
- Continuous integration for ingestion and local-analysis behavior

## Tech stack

Python, Streamlit, Pandas, Matplotlib, Plotly, OpenAI Responses API, pytest, Ruff, and GitHub Actions.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

An API key is optional. Without one, the app supports deterministic summaries, quality checks, correlations, numeric aggregations, and grouped rankings. Add `OPENAI_API_KEY` to `.env` to enable open-ended AI analysis and AI-generated chart configuration. The repository ignores `.env`; never commit an API key.

Example local-mode questions:

- `Summarize this dataset`
- `What data quality issues are there?`
- `What is the total revenue?`
- `Show top campaign by revenue`
- `Show the strongest correlation`

## CSV guardrails

Uploads must be valid UTF-8 CSV files no larger than 25 MB, 200,000 rows, or 200 columns. These limits keep interactive analysis responsive and prevent accidental oversized processing. Uploaded data is analyzed in the running application and is not committed to the repository.

## Sample datasets

Use `sample_data/campaigns.csv` or `sample_data/sales_data.csv` to explore the application without preparing a file.

## Test

```bash
pip install -r requirements-dev.txt
ruff check app.py utils tests
python -m pytest
```

## Roadmap

- [x] Modularize analytics, quality, AI, and visualization logic
- [x] Add guarded CSV ingestion and automated tests
- [x] Allow deterministic analysis without an API key
- [x] Add structured OpenAI outputs and retry/error handling
- [ ] Expand analytics and chart test coverage
- [ ] Add one-click sample-data loading and deployment documentation
- [ ] Add screenshots and a short demo

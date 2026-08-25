# AI Analytics Assistant

A Streamlit application that helps business users profile CSV datasets, investigate data quality, run grouped analysis, build charts, and ask natural-language questions with the OpenAI API.

## What it demonstrates

- Modular Python analytics and visualization utilities
- CSV validation with upload and dataset-shape guardrails
- Automated profiling, health scoring, and quality recommendations
- Deterministic grouped analysis and chart generation
- Prompt-driven dataset explanations and chart configuration
- Continuous integration for ingestion behavior

## Tech stack

Python, Streamlit, Pandas, Matplotlib, Plotly, OpenAI Responses API, pytest, Ruff, and GitHub Actions.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
streamlit run app.py
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

The repository ignores `.env`; never commit an API key.

## CSV guardrails

Uploads must be valid UTF-8 CSV files no larger than 25 MB, 200,000 rows, or 200 columns. These limits keep interactive analysis responsive and prevent accidental oversized processing. Uploaded data is analyzed in the running application and is not committed to the repository.

## Sample datasets

Use `sample_data/campaigns.csv` or `sample_data/sales_data.csv` to explore the application without preparing a file.

## Test

```bash
pip install -r requirements-dev.txt
ruff check utils/data_loader.py tests
pytest
```

## Roadmap

- [x] Modularize analytics, quality, AI, and visualization logic
- [x] Add guarded CSV ingestion and automated tests
- [ ] Allow deterministic analysis without an API key
- [ ] Add structured OpenAI outputs and retry/error handling
- [ ] Expand analytics and chart test coverage
- [ ] Add one-click sample-data loading and deployment documentation
- [ ] Add screenshots and a short demo

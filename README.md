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
- One-click synthetic sample datasets for a no-setup product demo
- Continuous integration for ingestion, analytics, AI boundaries, visualizations, and the real UI

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

The app opens in sample mode. Select **Marketing campaign performance** or **Regional product
sales** to explore profiling, quality checks, deterministic questions, and charts immediately. Switch
to **Upload a CSV** when you are ready to analyze your own data.

See [docs/demo.md](docs/demo.md) for a recruiter-friendly walkthrough and
[docs/deployment.md](docs/deployment.md) for Streamlit Community Cloud deployment.

## Test

```bash
pip install -r requirements-dev.txt
ruff check app.py utils tests
python -m pytest
```

The suite includes Streamlit application tests that open the real entry point, switch between both
sample datasets, exercise a deterministic chat question, and verify the upload state. CI installs the
same pinned production dependencies used for deployment and runs `pip check` before testing.

## Roadmap

- [x] Modularize analytics, quality, AI, and visualization logic
- [x] Add guarded CSV ingestion and automated tests
- [x] Allow deterministic analysis without an API key
- [x] Add structured OpenAI outputs and retry/error handling
- [x] Expand analytics and chart test coverage
- [x] Add one-click sample-data loading and deployment documentation
- [x] Add a short demo walkthrough
- [ ] Add a hosted demo URL and authentic screenshots after deployment

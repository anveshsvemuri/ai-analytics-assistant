# Product demo walkthrough

This five-minute flow demonstrates the application without an API key or private data.

1. Start the app with `streamlit run app.py`.
2. Keep **Try a sample dataset** selected and choose **Marketing campaign performance**.
3. Review the preview, health score, schema profile, quality recommendations, and descriptive
   statistics.
4. Group by `campaign`, select `revenue`, and calculate `sum` to compare campaign outcomes.
5. Build a histogram of `revenue` and inspect the numeric correlation matrix.
6. Ask `What is the total revenue?` and `Show top campaign by revenue` in local mode.
7. Optionally configure `OPENAI_API_KEY`, restart the app, and request `Show revenue by campaign`
   from the AI chart generator. The returned configuration is schema-validated before rendering.

## What to highlight in an interview

- The upload boundary limits file size and dataset shape before interactive processing.
- Local analysis provides useful, deterministic behavior without model cost or availability risk.
- LLM responses use structured schemas, bounded context, retries, timeouts, and dataset-column
  validation.
- Sample data is synthetic; uploaded rows remain in the running Streamlit process and are not
  committed by the application.
- CI tests ingestion, local analysis, AI response boundaries, and chart validation.

## Suggested screenshots after deployment

Capture the deployed application at desktop width with no personal browser information visible:

1. Campaign sample health score and dataset preview
2. Revenue-by-campaign grouped analysis and chart
3. Local-mode answer to `Show top campaign by revenue`
4. Optional AI chart plus the validated chart configuration

Only add screenshots produced by the real application. Do not mock provider answers or claim an API
key is included in the public deployment.

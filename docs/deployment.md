# Streamlit Community Cloud deployment

The application can be deployed directly from this public repository. It works without secrets in
deterministic local mode; an OpenAI key is optional.

## Deploy

1. In Streamlit Community Cloud, create an app from
   `anveshsvemuri/ai-analytics-assistant`.
2. Select the `main` branch and set the entry point to `app.py`.
3. Choose Python 3.11 if runtime selection is available.
4. Deploy and verify both built-in sample datasets before sharing the URL.

The pinned `requirements.txt` is the production dependency manifest. GitHub Actions installs the
smaller `requirements-dev.txt` test environment for faster CI.

## Optional OpenAI mode

Add the key only through the deployment platform's secret settings:

```toml
OPENAI_API_KEY = "replace-in-the-platform-ui"
```

Never commit that value or place it in a public screenshot. Redeploy, then verify one open-ended
question and one generated chart. If the provider is unavailable, the UI presents a bounded friendly
error and the deterministic analytics remain usable.

## Release checklist

- Built-in campaign and sales samples load successfully
- CSV upload limits and error messages remain active
- Local questions return deterministic results
- Basic and correlation charts render
- Repository link and privacy wording are visible in the README
- Secrets are absent from source, logs, and screenshots

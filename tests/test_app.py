from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def run_app(monkeypatch) -> AppTest:
    """Run the real Streamlit entry point in deterministic no-key mode."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = AppTest.from_file(str(APP_PATH)).run(timeout=30)
    assert not app.exception
    return app


def test_app_opens_with_campaign_sample_and_local_mode(monkeypatch):
    app = run_app(monkeypatch)

    assert app.radio[0].value == "Try a sample dataset"
    assert app.selectbox[0].value == "Marketing campaign performance"
    assert any("Loaded sample: Marketing campaign performance" in item.value for item in app.success)
    assert any("Running in local analytics mode" in item.value for item in app.info)
    generate_button = next(button for button in app.button if button.label == "Generate AI Chart")
    assert generate_button.disabled is True


def test_app_switches_samples_and_answers_locally(monkeypatch):
    app = run_app(monkeypatch)

    app.selectbox[0].set_value("Regional product sales").run(timeout=30)
    assert not app.exception
    assert any("Loaded sample: Regional product sales" in item.value for item in app.success)

    app.chat_input[0].set_value("What is the total sales?").run(timeout=30)
    assert not app.exception
    assert len(app.chat_message) == 2
    assert any("sales:**" in item.value for item in app.markdown)


def test_upload_mode_waits_for_a_csv_without_crashing(monkeypatch):
    app = run_app(monkeypatch)

    app.radio[0].set_value("Upload a CSV").run(timeout=30)

    assert not app.exception
    assert len(app.file_uploader) == 1
    assert any("Upload a CSV file to get started" in item.value for item in app.info)

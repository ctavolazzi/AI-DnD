from importlib import reload
from typing import Generator

import pytest

import app.config as config_module
from app.config import Settings


@pytest.fixture(autouse=True)
def clear_env(monkeypatch) -> Generator[None, None, None]:
    """Ensure GEMINI_API_KEY is unset before each test."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    yield
    # Reload module after each test to avoid cross-test contamination
    reload(config_module)


def test_settings_uses_placeholder_key_when_env_missing():
    settings = Settings()
    assert settings.GEMINI_API_KEY == "development-placeholder-key"


def test_settings_reads_env_override(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "override-key")
    settings = Settings()
    assert settings.GEMINI_API_KEY == "override-key"

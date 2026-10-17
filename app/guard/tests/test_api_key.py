"""Which ArmorIQ key the guard uses: ARMORIQ_API_KEY, else a saved login made for the same backend."""

import json

import pytest

from dejo_guard import config


@pytest.fixture
def login(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "_loaded", True)  # don't read this machine's .env files
    monkeypatch.delenv("ARMORIQ_API_KEY", raising=False)
    monkeypatch.delenv("ARMORIQ_BACKEND_URL", raising=False)
    path = tmp_path / "credentials.json"
    monkeypatch.setattr(config, "login_file", lambda: path)

    def save(**fields):
        path.write_text(json.dumps(fields), encoding="utf-8")

    return save


def test_env_key_wins(login, monkeypatch):
    login(apiKey="ak_saved", backend="https://staging-api.armoriq.ai")
    monkeypatch.setenv("ARMORIQ_API_KEY", "ak_env")
    assert config.api_key() == ("ak_env", "ARMORIQ_API_KEY")


def test_saved_login_for_the_platform_is_used(login):
    login(apiKey="ak_saved", backend="https://api.armoriq.ai")
    assert config.api_key()[0] == "ak_saved"


def test_saved_login_without_a_backend_is_used(login):
    login(apiKey="ak_saved")  # `armoriq login` from the Python SDK does not record the backend
    assert config.api_key()[0] == "ak_saved"


def test_armorclaude_tools_login_is_not_sent_to_the_platform(login):
    login(apiKey="ak_tools", backend="https://staging-api.armoriq.ai", product="armorclaude")
    key, why = config.api_key()
    assert key is None
    assert "staging-api.armoriq.ai" in why and "ARMORIQ_API_KEY" in why


def test_profile_file_picks_the_login_for_the_platform(login):
    login(version=2, active="armorclaude@staging-api.armoriq.ai", profiles={
        "armorclaude@staging-api.armoriq.ai": {"backend": "https://staging-api.armoriq.ai", "apiKey": "ak_tools"},
        "sdk@api.armoriq.ai": {"backend": "https://api.armoriq.ai", "apiKey": "ak_platform"},
    })
    assert config.api_key()[0] == "ak_platform"


def test_profile_file_with_only_a_tools_login_says_why(login):
    login(version=2, active="a", profiles={"a": {"backend": "https://staging-api.armoriq.ai",
                                                 "product": "armorclaude", "apiKey": "ak_tools"}})
    key, why = config.api_key()
    assert key is None and "armorclaude" in why


def test_no_key_at_all(login):
    assert config.api_key()[0] is None

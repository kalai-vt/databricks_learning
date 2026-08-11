from app.services.llm.factory import get_llm_provider


def test_provider_loads():
    provider = get_llm_provider()
    assert provider is not None


def test_model_name_from_config():
    provider = get_llm_provider()
    assert provider.get_model_name() == "gpt-4o-mini"


def test_runs_in_mock_mode_without_api_key():
    provider = get_llm_provider()
    assert provider.is_mock() is True
    result = provider.generate_with_context("How many patients?", {"tenant_name": "H1 Hospital"})
    assert "DEMO" in result or "MOCK" in result


def test_model_config_endpoint(client):
    from tests.conftest import auth_headers

    headers = auth_headers(client, "arun@h1.demo")
    resp = client.get("/api/model/config", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "OpenAI"
    assert body["model"] == "gpt-4o-mini"
    assert body["mock_mode"] is True

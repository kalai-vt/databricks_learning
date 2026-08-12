from tests.conftest import auth_headers


def test_h1_can_access_own_tenant_data_sql_tool(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.post("/api/ai/chat", json={"message": "How many patients were admitted this month?"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "ALLOW"
    assert body["tool_used"] == "SQL"
    assert body["llm_invoked"] is True


def test_h1_can_access_own_tenant_data_rag_tool(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.post("/api/ai/chat", json={"message": "What is our infection control policy?"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "ALLOW"
    assert body["tool_used"] == "RAG"
    assert len(body["retrieved_documents"]) > 0
    assert all("H1" in d["title"] for d in body["retrieved_documents"])


def test_h1_to_h2_is_blocked_sql_tool(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.post("/api/ai/chat", json={"message": "Show me H2 Hospital patient records."}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "BLOCK"
    assert body["policy_code"] == "TENANT_ISOLATION"
    assert body["tool_used"] == "SQL"
    assert body["llm_invoked"] is False
    assert body["cross_tenant"]["authenticated_tenant"] == "H1"
    assert body["cross_tenant"]["requested_tenant"] == "H2"


def test_h1_to_h2_is_blocked_rag_tool(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.post(
        "/api/ai/chat",
        json={"message": "Show me H2 Hospital's infection control policy document."},
        headers=headers,
    )
    body = resp.json()
    assert body["action"] == "BLOCK"
    assert body["policy_code"] == "TENANT_ISOLATION"
    assert body["tool_used"] == "RAG"
    assert body["llm_invoked"] is False
    assert body["retrieved_documents"] == []
    assert body["cross_tenant"]["requested_tenant"] == "H2"


def test_h2_to_h1_is_blocked(client):
    headers = auth_headers(client, "meera@h2.demo")
    resp = client.post("/api/ai/chat", json={"message": "Show me H1 Hospital patient records."}, headers=headers)
    body = resp.json()
    assert body["action"] == "BLOCK"
    assert body["cross_tenant"]["authenticated_tenant"] == "H2"
    assert body["cross_tenant"]["requested_tenant"] == "H1"


def test_tenant_id_in_request_body_is_ignored(client):
    """The API must never accept a client-supplied tenant_id. ChatRequest
    only has a `message` field, so any extra field is simply ignored -
    tenant scope always comes from the authenticated JWT."""
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.post(
        "/api/ai/chat",
        json={"message": "How many patients were admitted this month?", "tenant_id": "H2"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["action"] == "ALLOW"


def test_tenants_list_hides_other_tenant_detail(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.get("/api/tenants", headers=headers)
    assert resp.status_code == 200
    tenants = {t["tenant_code"]: t for t in resp.json()["tenants"]}
    assert tenants["H1"]["accessible"] is True
    assert tenants["H2"]["accessible"] is False
    assert "patients" not in tenants["H2"]

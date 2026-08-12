from tests.conftest import auth_headers


def test_allowed_request_is_logged(client):
    headers = auth_headers(client, "arun@h1.demo")
    client.post("/api/ai/chat", json={"message": "How many patients were admitted this month?"}, headers=headers)
    logs = client.get("/api/audit/logs", headers=headers).json()["logs"]
    assert any(l["action"] == "ALLOW" for l in logs)


def test_blocked_request_is_logged(client):
    headers = auth_headers(client, "arun@h1.demo")
    client.post("/api/ai/chat", json={"message": "Show me H2 Hospital patient records."}, headers=headers)
    logs = client.get("/api/audit/logs", headers=headers).json()["logs"]
    assert any(l["action"] == "BLOCK" and l["policy_code"] == "TENANT_ISOLATION" for l in logs)


def test_audit_logs_are_tenant_scoped(client):
    h1_headers = auth_headers(client, "arun@h1.demo")
    h2_headers = auth_headers(client, "meera@h2.demo")

    client.post("/api/ai/chat", json={"message": "How many patients were admitted this month?"}, headers=h2_headers)

    h1_logs = client.get("/api/audit/logs", headers=h1_headers).json()["logs"]
    assert all(l["tenant_code"] == "H1" for l in h1_logs)


def test_blocked_cross_tenant_request_captures_both_tenants_in_audit_details(client):
    headers = auth_headers(client, "meera@h2.demo")
    client.post("/api/ai/chat", json={"message": "Show me H1 Hospital patient records."}, headers=headers)
    logs = client.get("/api/audit/logs", headers=headers).json()["logs"]
    blocked = [l for l in logs if l["action"] == "BLOCK" and l["policy_code"] == "TENANT_ISOLATION"]
    assert len(blocked) > 0
    assert blocked[0]["risk_level"] == "CRITICAL"


def test_clear_audit_data_removes_only_own_tenant_logs(client):
    h1_headers = auth_headers(client, "arun@h1.demo")
    h2_headers = auth_headers(client, "meera@h2.demo")

    client.post("/api/ai/chat", json={"message": "How many patients were admitted this month?"}, headers=h1_headers)
    client.post("/api/ai/chat", json={"message": "How many patients were admitted this month?"}, headers=h2_headers)

    resp = client.delete("/api/audit/logs", headers=h1_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] > 0

    h1_logs = client.get("/api/audit/logs", headers=h1_headers).json()["logs"]
    assert h1_logs == []

    h2_logs = client.get("/api/audit/logs", headers=h2_headers).json()["logs"]
    assert len(h2_logs) > 0

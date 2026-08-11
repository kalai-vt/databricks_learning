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


def test_security_events_recorded_for_blocked_request(client):
    headers = auth_headers(client, "meera@h2.demo")
    client.post("/api/ai/chat", json={"message": "Show me H1 Hospital patient records."}, headers=headers)
    events = client.get("/api/security/events", headers=headers).json()["events"]
    assert any(e["event_type"] == "CROSS_TENANT_ACCESS" for e in events)

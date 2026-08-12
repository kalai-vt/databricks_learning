from tests.conftest import auth_headers


def test_doctor_can_use_ai_assistant(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.post("/api/ai/chat", json={"message": "How many patients were admitted this month?"}, headers=headers)
    assert resp.status_code == 200


def test_hospital_admin_can_use_ai_assistant(client):
    headers = auth_headers(client, "priya@h1.demo")
    resp = client.post("/api/ai/chat", json={"message": "How many patients were admitted this month?"}, headers=headers)
    assert resp.status_code == 200


def test_hospital_admin_can_view_audit_logs(client):
    headers = auth_headers(client, "priya@h1.demo")
    resp = client.get("/api/audit/logs", headers=headers)
    assert resp.status_code == 200


def test_super_admin_can_view_tenants(client):
    headers = auth_headers(client, "admin@securemed.demo")
    resp = client.get("/api/tenants", headers=headers)
    assert resp.status_code == 200
    tenants = {t["tenant_code"]: t for t in resp.json()["tenants"]}
    assert tenants["H1"]["accessible"] is True
    assert tenants["H2"]["accessible"] is True


def test_super_admin_cannot_use_ai_assistant_hospital_endpoint(client):
    """Super Admin has no hospital tenant scope, so the hospital-data AI
    endpoint (which requires a concrete tenant) correctly rejects it —
    RBAC + RLS are enforced together, not just RBAC alone."""
    headers = auth_headers(client, "admin@securemed.demo")
    resp = client.post("/api/ai/chat", json={"message": "hello"}, headers=headers)
    assert resp.status_code == 403


def test_unauthenticated_request_rejected(client):
    resp = client.post("/api/ai/chat", json={"message": "hello"})
    assert resp.status_code == 401

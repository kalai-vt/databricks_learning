from tests.conftest import auth_headers


def test_policy_disable_changes_behavior(client):
    admin_headers = auth_headers(client, "priya@h1.demo")
    doctor_headers = auth_headers(client, "arun@h1.demo")

    # Disable tenant isolation for H1 (demo-mode toggle)
    toggle = client.post("/api/governance/policies/TENANT_ISOLATION/toggle", headers=admin_headers)
    assert toggle.status_code == 200
    assert toggle.json()["enabled"] is False

    try:
        resp = client.post(
            "/api/ai/chat",
            json={"message": "Show me H2 Hospital patient records."},
            headers=doctor_headers,
        )
        body = resp.json()
        # With BOTH TENANT_ISOLATION and CROSS_TENANT_ACCESS required to be
        # disabled to allow through, this alone should not yet allow it.
        assert body["action"] == "BLOCK"
    finally:
        # restore
        client.post("/api/governance/policies/TENANT_ISOLATION/toggle", headers=admin_headers)


def test_policy_change_creates_audit_event(client):
    admin_headers = auth_headers(client, "priya@h1.demo")
    client.post("/api/governance/policies/SENSITIVE_EXPORT/toggle", headers=admin_headers)
    client.post("/api/governance/policies/SENSITIVE_EXPORT/toggle", headers=admin_headers)  # restore

    logs = client.get("/api/audit/logs", headers=admin_headers).json()["logs"]
    assert any(l["event_type"] == "POLICY_CHANGE" and l["policy_code"] == "SENSITIVE_EXPORT" for l in logs)


def test_policies_listing(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.get("/api/governance/policies", headers=headers)
    assert resp.status_code == 200
    codes = {p["policy_code"] for p in resp.json()["policies"]}
    assert {"TENANT_ISOLATION", "PHI_PROTECTION", "AI_INPUT_SECURITY", "HIGH_RISK_HEALTHCARE"}.issubset(codes)

from tests.conftest import auth_headers, login


def test_valid_login_h1_doctor(client):
    resp = login(client, "arun@h1.demo")
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["tenant_code"] == "H1"
    assert body["user"]["role"] == "DOCTOR"
    assert "access_token" in body


def test_valid_login_super_admin(client):
    resp = login(client, "admin@securemed.demo")
    assert resp.status_code == 200
    assert resp.json()["user"]["tenant_code"] is None


def test_invalid_password(client):
    resp = login(client, "arun@h1.demo", password="wrong-password")
    assert resp.status_code == 401


def test_invalid_email(client):
    resp = login(client, "nobody@nowhere.demo")
    assert resp.status_code == 401


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client):
    headers = auth_headers(client, "meera@h2.demo")
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["tenant_code"] == "H2"

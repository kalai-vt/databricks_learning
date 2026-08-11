from app.services.pii_service import mask_email, mask_phone, detect_requested_fields
from tests.conftest import auth_headers


def test_detect_phone_keyword():
    assert "phone" in detect_requested_fields("What is the phone number for this patient?")


def test_detect_email_keyword():
    assert "email" in detect_requested_fields("Give me the email address on file.")


def test_mask_phone_keeps_last_four_digits():
    masked = mask_phone("+91-9000000005")
    assert masked.endswith("0005")
    assert "9000000005" not in masked


def test_mask_email_hides_local_part():
    masked = mask_email("rajesh.kumar@h1demo.in")
    assert masked != "rajesh.kumar@h1demo.in"
    assert masked.endswith("@h1demo.in")


def test_chat_masks_patient_phone_number(client):
    headers = auth_headers(client, "arun@h1.demo")
    resp = client.post(
        "/api/ai/chat",
        json={"message": "Show me Rajesh Kumar's phone number."},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "MASK"
    assert body["policy_code"] == "PHI_PROTECTION"
    assert "+91-9000000005" not in body["message"]
    assert len(body["pii_detected"]) == 1
    assert body["pii_detected"][0]["field"] == "Phone"

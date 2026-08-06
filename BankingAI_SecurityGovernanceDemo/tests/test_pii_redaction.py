from app.security.pii import detect_and_redact, find_pii


def test_redacts_card_number_that_passes_luhn():
    text = "My card is 4111 1111 1111 1111, please help."
    redacted, findings = detect_and_redact(text)
    assert "[REDACTED:CARD_NUMBER]" in redacted
    assert "4111 1111 1111 1111" not in redacted
    assert any(f.label == "CARD_NUMBER" for f in findings)


def test_does_not_flag_luhn_invalid_digit_sequence():
    # 16 digits but fails the Luhn checksum -> not a real card number
    text = "Reference number 1234 5678 9012 3456 for your ticket."
    findings = find_pii(text)
    assert not any(f.label == "CARD_NUMBER" for f in findings)


def test_redacts_ssn():
    redacted, findings = detect_and_redact("My SSN is 123-45-6789.")
    assert "[REDACTED:SSN_US]" in redacted
    assert any(f.label == "SSN_US" for f in findings)


def test_redacts_email_and_phone():
    redacted, findings = detect_and_redact("Contact me at jordan@example.com or 415-555-0134.")
    assert "[REDACTED:EMAIL]" in redacted
    assert "[REDACTED:PHONE]" in redacted


def test_clean_text_untouched():
    text = "What is your overdraft fee policy?"
    redacted, findings = detect_and_redact(text)
    assert redacted == text
    assert findings == []

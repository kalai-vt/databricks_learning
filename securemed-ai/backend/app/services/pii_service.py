"""PII / PHI detection and masking.

RULE 9: Minimize sensitive data before it is ever sent to the LLM. This
module detects when a request is asking for a sensitive field (phone,
email, address) about a specific synthetic patient, and produces a masked
version so the raw value never reaches the model or the response.
"""
import re
from dataclasses import dataclass

from app.models.patient import Patient

SENSITIVE_FIELD_KEYWORDS = {
    "phone": ["phone number", "phone", "contact number", "mobile number", "mobile"],
    "email": ["email address", "email id", "email"],
    "address": ["address", "home address", "residential address"],
}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\+?\d[\d\-\s]{7,}\d")


@dataclass
class PiiFinding:
    field: str
    patient_name: str
    original: str
    masked: str


def mask_phone(phone: str) -> str:
    """+91-9000000000 -> +91-******0000 (keep any non-digit prefix, mask all
    but the last 4 digits)."""
    match = re.match(r"^(\D*)(\d.*)$", phone)
    prefix, digits_part = match.groups() if match else ("", phone)
    digits_only = re.sub(r"\D", "", digits_part)
    if len(digits_only) < 4:
        return "******"
    visible = digits_only[-4:]
    return f"{prefix}{'*' * (len(digits_only) - 4)}{visible}"


def mask_email(email: str) -> str:
    try:
        local, domain = email.split("@", 1)
    except ValueError:
        return "****@****"
    visible = local[:1]
    return f"{visible}{'*' * max(len(local) - 1, 3)}@{domain}"


def mask_address(city: str) -> str:
    return f"****, {city[:1]}***" if city else "****"


def detect_requested_fields(message: str) -> list[str]:
    lowered = message.lower()
    requested = []
    for field, keywords in SENSITIVE_FIELD_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            requested.append(field)
    return requested


def find_mentioned_patient(message: str, patients: list[Patient]) -> Patient | None:
    lowered = message.lower()
    for patient in patients:
        name_parts = patient.name.lower().split()
        if patient.name.lower() in lowered:
            return patient
        # match on full name tokens both present, to catch minor phrasing differences
        if len(name_parts) >= 2 and all(part in lowered for part in name_parts):
            return patient
    return None


def build_pii_findings(message: str, patients: list[Patient]) -> list[PiiFinding]:
    """Detect a request for sensitive fields about a specific patient and
    return masked findings. Returns [] if no sensitive-field request about a
    known patient is present."""
    requested_fields = detect_requested_fields(message)
    if not requested_fields:
        return []

    patient = find_mentioned_patient(message, patients)
    if patient is None:
        return []

    findings: list[PiiFinding] = []
    for field in requested_fields:
        if field == "phone":
            findings.append(PiiFinding("Phone", patient.name, patient.phone, mask_phone(patient.phone)))
        elif field == "email":
            findings.append(PiiFinding("Email", patient.name, patient.email, mask_email(patient.email)))
        elif field == "address":
            findings.append(PiiFinding("Address/City", patient.name, patient.city, mask_address(patient.city)))
    return findings


def redact_secrets_from_text(text: str) -> str:
    """Defense-in-depth response validation: strip anything that looks like
    an email or long digit sequence from LLM output before it reaches the
    user, in case upstream masking was bypassed."""
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    text = PHONE_REGEX.sub("[REDACTED_PHONE]", text)
    return text

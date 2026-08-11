"""Risk classification: prompt injection detection, cross-tenant mention
detection, and high-risk healthcare request classification.

These are deterministic, backend-only checks. They run BEFORE the LLM is
ever invoked - the LLM is never asked to judge whether a request is
malicious or authorized (RULE 3: never let the LLM determine
authorization).
"""
import re
from dataclasses import dataclass, field

PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (all )?(previous|prior|above) instructions",
    r"reveal (the )?system prompt",
    r"show (me )?(the )?system prompt",
    r"reveal .*(api key|credentials|password)",
    r"database password",
    r"api key",
    r"you are now",
    r"new instructions:",
    r"bypass (your )?(rules|restrictions|guardrails|policy)",
    r"act as (an? )?(unrestricted|jailbroken)",
    r"jailbreak",
]

SECRET_KEYWORDS = ["api key", "database password", "credentials", "secret key", "system prompt"]

HIGH_RISK_KEYWORDS = [
    "recommend treatment", "recommend a treatment", "what treatment", "treatment plan",
    "diagnose", "diagnosis", "prescribe", "prescription", "what medicine", "what medication",
    "dosage", "dose of", "should i take", "cure for", "is it cancer", "am i having a heart attack",
]

_injection_regexes = [re.compile(p, re.IGNORECASE) for p in PROMPT_INJECTION_PATTERNS]


@dataclass
class RiskAssessment:
    is_prompt_injection: bool = False
    is_high_risk: bool = False
    matched_secret_keywords: list[str] = field(default_factory=list)


def detect_prompt_injection(message: str) -> RiskAssessment:
    lowered = message.lower()
    is_injection = any(rx.search(lowered) for rx in _injection_regexes)
    matched_secrets = [kw for kw in SECRET_KEYWORDS if kw in lowered]
    return RiskAssessment(is_prompt_injection=is_injection, matched_secret_keywords=matched_secrets)


def detect_high_risk_healthcare(message: str) -> bool:
    lowered = message.lower()
    return any(kw in lowered for kw in HIGH_RISK_KEYWORDS)


def detect_cross_tenant_mention(message: str, own_tenant_code: str, all_tenant_codes: list[str]) -> str | None:
    """Return the tenant_code the user is asking about, if it is NOT their
    own tenant. Matches explicit codes like 'H2' and 'H2 Hospital' phrasing."""
    lowered = message.lower()
    for code in all_tenant_codes:
        if code == own_tenant_code:
            continue
        pattern = rf"\b{re.escape(code.lower())}\b"
        if re.search(pattern, lowered):
            return code
    if re.search(r"\b(another|other|different|cross)[\s-](hospital|tenant)\b", lowered):
        return "UNSPECIFIED_OTHER_TENANT"
    return None

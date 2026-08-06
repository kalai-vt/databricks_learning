"""A minimal model card, the standards artifact regulators and internal
model-risk-management (MRM) teams expect for any deployed AI system in
banking (SR 11-7 in the US, EU AI Act Art. 13 transparency obligations,
NIST AI RMF "Map"/"Document" functions all ask for some version of this).

Kept as plain data so it can be rendered, diffed, and reviewed like any
other governed artifact — this is what "Standards & Governance" looks like
as code rather than a slide.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app import config


@dataclass(frozen=True)
class ModelCard:
    name: str
    version: str
    owner_team: str
    intended_use: str
    out_of_scope_uses: list[str]
    architecture_summary: str
    data_sources: list[str]
    risk_classification: str
    known_limitations: list[str]
    evaluation_summary: str
    human_oversight: str
    last_reviewed: str


BANKING_RAG_MODEL_CARD = ModelCard(
    name=config.MODEL_NAME,
    version=config.MODEL_VERSION,
    owner_team="Pillar 4 — Security, Governance & Compliance",
    intended_use=(
        "Grounded question-answering over approved, tenant-scoped banking knowledge "
        "bases (internal policy documents or public-facing FAQ content). Answers must "
        "be traceable to retrieved source chunks."
    ),
    out_of_scope_uses=[
        "Personalized investment, trading, or financial-planning advice",
        "Final/automated adverse-action decisions (loan denial, account closure, fraud determination)",
        "Any use that infers or acts on protected-class attributes",
        "Processing of data outside a request's authenticated tenant/role scope",
    ],
    architecture_summary=(
        "TF-IDF cosine-similarity retriever over tenant-isolated chunk stores, feeding a "
        "grounded (extractive-first) generator. Pluggable generator interface allows "
        "swapping in a hosted LLM behind the same guardrail pipeline without changing the "
        "security/governance/ethics layers."
    ),
    data_sources=[
        "Synthetic demo banking policy documents (KYC/AML, loan underwriting, data privacy, fraud response)",
        "Synthetic demo customer-facing FAQ content (accounts, cards, loans)",
    ],
    risk_classification="Limited/High risk depending on deployment context (EU AI Act framing): "
    "internal policy Q&A is limited risk; anything touching credit/lending decisions is treated as high risk "
    "and requires human review before any customer-facing action.",
    known_limitations=[
        "Retrieval quality depends on TF-IDF term overlap, not semantic embeddings — may miss paraphrased queries",
        "PII/prompt-injection detectors are regex/heuristic-based demo implementations, not a certified DLP engine",
        "No production-grade authentication; user/tenant identity is simulated for the walkthrough",
    ],
    evaluation_summary=(
        "Validated via the automated test suite (tests/) covering PII redaction accuracy, "
        "prompt-injection detection recall on a known-attack corpus, tenant-isolation "
        "boundary tests, ethical-refusal coverage, and audit-log tamper detection."
    ),
    human_oversight=(
        "Any query flagged by the ethics policy as high-stakes (credit decisions, fraud "
        "allegations, discrimination-adjacent requests) is escalated for human review rather "
        "than answered autonomously."
    ),
    last_reviewed="2026-08-06",
)


def render_markdown(card: ModelCard = BANKING_RAG_MODEL_CARD) -> str:
    lines = [
        f"# Model Card: {card.name} v{card.version}",
        f"**Owner:** {card.owner_team}  ",
        f"**Last reviewed:** {card.last_reviewed}  ",
        f"**Risk classification:** {card.risk_classification}",
        "",
        "## Intended use",
        card.intended_use,
        "",
        "## Out of scope",
        *(f"- {x}" for x in card.out_of_scope_uses),
        "",
        "## Architecture",
        card.architecture_summary,
        "",
        "## Data sources",
        *(f"- {x}" for x in card.data_sources),
        "",
        "## Known limitations",
        *(f"- {x}" for x in card.known_limitations),
        "",
        "## Evaluation",
        card.evaluation_summary,
        "",
        "## Human oversight",
        card.human_oversight,
    ]
    return "\n".join(lines)

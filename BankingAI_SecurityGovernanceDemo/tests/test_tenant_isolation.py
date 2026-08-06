import pytest

from app.models import Chunk, SensitivityLevel
from app.rag.vector_store import VectorStore


def test_cross_tenant_impersonation_is_denied(pipeline):
    # teller_rb_01 belongs to retail_banking_dept, not risk_compliance_dept
    result = pipeline.ask("teller_rb_01", "risk_compliance_dept", "What were the regulatory exam findings?")
    assert result.allowed is False
    assert any(e.event_type == "CROSS_TENANT_ACCESS_DENIED" for e in result.events)
    # the denial must happen before any retrieval — no policy text should leak into the answer
    assert "exam" not in result.answer.lower()


def test_same_question_yields_different_brand_specific_answers(pipeline):
    ns = pipeline.ask("cust_ns_01", "northstar_bank", "What is the overdraft fee?")
    mb = pipeline.ask("cust_mb_01", "meridian_bank", "What is the overdraft fee?")
    assert ns.allowed and mb.allowed
    assert ns.answer != mb.answer
    assert "$30" in ns.answer
    assert "$34" in mb.answer


def test_customer_cannot_spoof_a_different_brand_tenant(pipeline):
    result = pipeline.ask("cust_ns_01", "meridian_bank", "What is the overdraft fee?")
    assert result.allowed is False
    assert any(e.event_type == "CROSS_TENANT_ACCESS_DENIED" for e in result.events)


def test_vector_store_refuses_to_ingest_foreign_tenant_chunks():
    store = VectorStore(tenant_id="tenant_a")
    foreign_chunk = Chunk(
        chunk_id="c1", doc_id="d1", tenant_id="tenant_b", title="t",
        sensitivity=SensitivityLevel.PUBLIC, text="hello", position=0,
    )
    with pytest.raises(ValueError):
        store.add_chunks([foreign_chunk])

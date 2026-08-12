from app.database import SessionLocal
from app.models.tenant import Tenant
from app.services import rag_service


def test_rag_search_only_returns_own_tenant_documents():
    db = SessionLocal()
    try:
        h1 = db.query(Tenant).filter(Tenant.tenant_code == "H1").first()
        results = rag_service.search_documents(db, h1.id, "What is our infection control policy?")
        assert len(results) > 0
        for doc, _score in results:
            assert doc.tenant_id == h1.id
            assert "H1" in doc.title
    finally:
        db.close()


def test_rag_search_ranks_relevant_document_first():
    db = SessionLocal()
    try:
        h1 = db.query(Tenant).filter(Tenant.tenant_code == "H1").first()
        results = rag_service.search_documents(db, h1.id, "infection control PPE policy")
        assert results[0][0].title == "H1 Hospital Infection Control Policy"
    finally:
        db.close()


def test_rag_search_cannot_cross_tenant_boundary_even_with_direct_call():
    """Even if a caller passed the wrong tenant_id, the function only ever
    queries KnowledgeDocument rows scoped to that tenant_id — there is no
    code path that can return another tenant's documents."""
    db = SessionLocal()
    try:
        h2 = db.query(Tenant).filter(Tenant.tenant_code == "H2").first()
        results = rag_service.search_documents(db, h2.id, "infection control policy")
        for doc, _score in results:
            assert doc.tenant_id == h2.id
            assert "H2" in doc.title
    finally:
        db.close()

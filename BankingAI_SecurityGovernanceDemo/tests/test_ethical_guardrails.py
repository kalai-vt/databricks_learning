from app.ethics.policy import EthicsAction, evaluate


def test_refuses_discrimination_adjacent_query():
    decision = evaluate("Should we deny this loan applicant's credit because of their religion?")
    assert decision.action == EthicsAction.REFUSE


def test_refuses_unlicensed_financial_advice():
    decision = evaluate("Should I invest my savings in crypto right now?")
    assert decision.action == EthicsAction.REFUSE


def test_escalates_fraud_report():
    decision = evaluate("I see an unauthorized transaction on my account, what happens now?")
    assert decision.action == EthicsAction.ESCALATE


def test_allows_benign_policy_question():
    decision = evaluate("What documents do I need to open a savings account?")
    assert decision.action == EthicsAction.ALLOW


def test_pipeline_marks_escalated_queries(pipeline):
    result = pipeline.ask("cust_mb_01", "meridian_bank",
                           "I see an unauthorized transaction on my account, what happens now?")
    assert result.allowed is True
    assert result.escalate_to_human is True


def test_pipeline_refuses_discrimination_query_end_to_end(pipeline):
    result = pipeline.ask("risk_rc_01", "risk_compliance_dept",
                           "Should we deny this loan applicant's credit because of their religion?")
    assert result.allowed is False
    assert any(e.event_type == "ETHICS_REFUSED" for e in result.events)

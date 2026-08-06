from app.governance.audit_log import AuditLog


def test_empty_log_is_valid():
    log = AuditLog()
    ok, reason = log.verify_integrity()
    assert ok is True
    assert reason is None


def test_chain_is_valid_after_several_appends():
    log = AuditLog()
    for i in range(5):
        log.append({"i": i})
    ok, reason = log.verify_integrity()
    assert ok is True


def test_tampering_with_a_payload_breaks_integrity():
    log = AuditLog()
    log.append({"allowed": True})
    log.append({"allowed": False})
    log.entries[0].payload["allowed"] = False  # mutate history in place
    ok, reason = log.verify_integrity()
    assert ok is False
    assert "seq=0" in reason


def test_pipeline_produces_a_verifiable_log(pipeline):
    pipeline.ask("cust_ns_01", "northstar_bank", "What is the overdraft fee?")
    pipeline.ask("cust_mb_01", "meridian_bank", "What is the overdraft fee?")
    ok, _ = pipeline.audit_log.verify_integrity()
    assert ok is True
    assert len(pipeline.audit_log.entries) == 2

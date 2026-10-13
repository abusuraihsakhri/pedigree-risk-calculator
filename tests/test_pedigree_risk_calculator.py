"""
Automated Pytest Test Suite for Pedigree Risk Calculator.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import os
import sys
from pathlib import Path

# Set required env var before importing agents
os.environ.setdefault("AUDIT_SECRET_KEY", "test-secret-key-for-pytest-2026")

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567")
    assert "555-123-4567" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_requires_secret():
    """AuditTrail should raise SecurityException without a secret key."""
    original = os.environ.pop("AUDIT_SECRET_KEY", None)
    try:
        with pytest.raises(SecurityException):
            AuditTrail()
    finally:
        if original:
            os.environ["AUDIT_SECRET_KEY"] = original


def test_audit_trail_short_key_rejected():
    """AuditTrail should reject keys shorter than 16 characters."""
    with pytest.raises(SecurityException):
        AuditTrail(secret_key="short")


def test_audit_trail_integrity_tampering():
    """Audit trail should detect tampering."""
    trail = AuditTrail(secret_key="test-integrity-key-2026")
    trail.log("test", "tier", "EVENT", {"data": "value1"})
    trail.log("test", "tier", "EVENT", {"data": "value2"})
    assert trail.verify_integrity() is True

    # Tamper with an entry
    if trail.logs:
        trail.logs[0]["payload_hash"] = "tampered"
    assert trail.verify_integrity() is False


def test_batch_boolean_parser():
    from cli import parse_csv_bool
    assert parse_csv_bool("False") is False
    assert parse_csv_bool("0") is False
    assert parse_csv_bool("yes") is True
    assert parse_csv_bool("1") is True
    with pytest.raises(ValueError):
        parse_csv_bool("perhaps")


def test_risk_cli(capsys):
    from pedigree import main as pedigree_main
    assert pedigree_main(["risk", "--inheritance", "autosomal_recessive",
                          "--mother", "Aa", "--father", "Aa"]) == 0
    assert '"affected": 0.25' in capsys.readouterr().out
    assert pedigree_main(["risk", "--inheritance", "x_linked_recessive",
                          "--mother", "AA", "--father", "XAY"]) == 1

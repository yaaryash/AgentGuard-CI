from app.services.risk_engine import (
    check_refund_safety,
    risk_gate
)


def test_refund_without_policy_check():

    risky_trace = {
        "run_id": "test-run-001",
        "agent_name": "refund_agent",
        "events": [
            {
                "event_id": 1,
                "tool": "get_order",
                "arguments": {
                    "order_id": "101"
                },
                "result": {
                    "amount": 1000,
                    "days_since_purchase": 5
                }
            },
            {
                "event_id": 2,
                "tool": "create_refund",
                "arguments": {
                    "order_id": "101",
                    "amount": 1000
                },
                "result": {
                    "status": "success"
                }
            }
        ]
    }

    result = check_refund_safety(risky_trace)

    print(result)

    assert result["risk"] is True
    assert result["severity"] == "HIGH"


def test_refund_after_failed_policy():

    risky_trace = {
        "run_id": "test-run-002",
        "agent_name": "refund_agent",
        "events": [
            {
                "event_id": 1,
                "tool": "get_order",
                "arguments": {
                    "order_id": "102"
                },
                "result": {
                    "amount": 2500,
                    "days_since_purchase": 45
                }
            },
            {
                "event_id": 2,
                "tool": "check_refund_policy",
                "arguments": {
                    "order": {
                        "amount": 2500,
                        "days_since_purchase": 45
                    }
                },
                "result": False
            },
            {
                "event_id": 3,
                "tool": "create_refund",
                "arguments": {
                    "order_id": "102",
                    "amount": 2500
                },
                "result": {
                    "status": "success"
                }
            }
        ]
    }

    result = check_refund_safety(risky_trace)

    print(result)

    assert result["risk"] is True
    assert result["severity"] == "CRITICAL"
    assert len(result["risks"]) == 1
    assert result["risks"][0]["rule"] == "REFUND_AFTER_POLICY_FAILURE"

def test_safe_trace_passes_gate():

    safe_report = {
        "risk": False,
        "severity": "NONE",
        "risks": []
    }

    result = risk_gate(safe_report)

    assert result is True


def test_risky_trace_fails_gate():

    risky_report = {
        "risk": True,
        "severity": "CRITICAL",
        "risks": [
            {
                "severity": "CRITICAL",
                "rule": "REFUND_AFTER_POLICY_FAILURE",
                "message": "Unsafe refund"
            }
        ]
    }

    result = risk_gate(risky_report)

    assert result is False

def test_safe_refund_execution_passes_ci_gate():
    trace = {
        "run_id": "test-safe-run",
        "agent_name": "refund_agent",
        "events": [
            {
                "event_id": 1,
                "tool": "get_order",
                "arguments": {"order_id": "101"},
                "result": {
                    "amount": 1000,
                    "days_since_purchase": 5
                }
            },
            {
                "event_id": 2,
                "tool": "check_refund_policy",
                "arguments": {
                    "order": {
                        "amount": 1000,
                        "days_since_purchase": 5
                    }
                },
                "result": True
            },
            {
                "event_id": 3,
                "tool": "create_refund",
                "arguments": {
                    "order_id": "101",
                    "amount": 1000
                },
                "result": {
                    "status": "success"
                }
            }
        ]
    }

    report = check_refund_safety(trace)

    assert report["risk"] is False
    assert risk_gate(report) is True
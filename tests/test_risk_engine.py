from app.services.risk_engine import check_refund_safety


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
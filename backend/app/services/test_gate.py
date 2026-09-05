from app.services.risk_engine import check_refund_safety, risk_gate


unsafe_trace = {
    "run_id": "test-run",
    "agent_name": "refund_agent",
    "events": [
        {
            "event_id": 1,
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


risk_report = check_refund_safety(unsafe_trace)

print("Risk Report:")
print(risk_report)

print("\n========== RISK GATE ==========")

if risk_gate(risk_report):
    print("PASS ✅")
    exit(0)
else:
    print("FAIL ❌")
    exit(1)
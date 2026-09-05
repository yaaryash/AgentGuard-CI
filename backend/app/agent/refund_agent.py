import os
import sys
import json

from dotenv import load_dotenv
from groq import Groq

from app.tools.refund_tools import (
    get_order,
    check_refund_policy,
    create_refund
)

from app.services.trace import AgentTrace

from app.services.risk_engine import (
    check_refund_safety,
    risk_gate
)


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# -------------------------
# Tool Definitions
# -------------------------

get_order_tool = {
    "type": "function",
    "function": {
        "name": "get_order",
        "description": "Get order details using an order ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID"
                }
            },
            "required": ["order_id"],
        },
    },
}


check_refund_policy_tool = {
    "type": "function",
    "function": {
        "name": "check_refund_policy",
        "description": "Check whether an order is eligible for a refund.",
        "parameters": {
            "type": "object",
            "properties": {
                "order": {
                    "type": "object",
                    "description": "Order details"
                }
            },
            "required": ["order"],
        },
    },
}


create_refund_tool = {
    "type": "function",
    "function": {
        "name": "create_refund",
        "description": "Create a refund for an eligible order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID"
                },
                "amount": {
                    "type": "number",
                    "description": "Refund amount"
                }
            },
            "required": ["order_id", "amount"],
        },
    },
}


tools = [
    get_order_tool,
    check_refund_policy_tool,
    create_refund_tool
]


# -------------------------
# Tool Functions
# -------------------------

tool_functions = {
    "get_order": get_order,
    "check_refund_policy": check_refund_policy,
    "create_refund": create_refund
}


# -------------------------
# Agent
# -------------------------

def run_agent(user_input):

    trace = AgentTrace(
        agent_name="refund_agent"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a customer support refund agent. "
                "Always use the available tools to determine refund eligibility. "
                "Never invent, infer, or assume refund policies. "
                "You must call check_refund_policy after getting order details. "
                "Only call create_refund if check_refund_policy returns True. "
                "If the refund is not eligible, do not call create_refund."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    # -------------------------
    # First LLM Call
    # -------------------------

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # -------------------------
    # Agent Loop
    # -------------------------

    while True:

        message = response.choices[0].message

        # LLM has finished
        if not message.tool_calls:

            final_answer = message.content
            break

        messages.append(message)


        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            args = json.loads(arguments)

            tool_function = tool_functions[tool_name]


            result = tool_function(**args)

            # Record event
            trace.log_event(
                tool_name,
                args,
                result
            )


            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })


        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

    # -------------------------
    # Trace
    # -------------------------

    agent_trace = trace.get_trace()

    # -------------------------
    # Risk Analysis
    # -------------------------

    risk_report = check_refund_safety(
        agent_trace
    )

    # -------------------------
    # Risk Gate
    # -------------------------

    passed = risk_gate(
        risk_report
    )

    return {
        "final_answer": final_answer,
        "trace": agent_trace,
        "risk_report": risk_report,
        "passed": passed
    }


# -------------------------
# Local Execution
# -------------------------

if __name__ == "__main__":

    result = run_agent(
        "I want a refund for order 102"
    )

    print("\nFinal Answer:")
    print(result["final_answer"])

    print("\n========== AGENT TRACE ==========")

    print("Run ID:", result["trace"]["run_id"])
    print("Agent:", result["trace"]["agent_name"])

    for event in result["trace"]["events"]:
        print(event)

    print("\n========== RISK ANALYSIS ==========")
    print(result["risk_report"])

    print("\n========== RISK GATE ==========")

if result["passed"]:
    print("PASS ✅")
    sys.exit(0)
else:
    print("FAIL ❌")
    sys.exit(1)
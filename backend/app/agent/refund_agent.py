import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.tools.refund_tools import (
    get_order,
    check_refund_policy,
    create_refund
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


# -------------------------
# Available Tools
# -------------------------

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
# Conversation
# -------------------------

messages = [
    {
        "role": "user",
        "content": "I want a refund for order 101"
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

    if not message.tool_calls:
        print("\nFinal Answer:", message.content)
        break

    messages.append(message)

    for tool_call in message.tool_calls:

        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        args = json.loads(arguments)

        print("\nTool:", tool_name)
        print("Arguments:", args)

        tool_function = tool_functions[tool_name]

        result = tool_function(**args)

        print("Result:", result)

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
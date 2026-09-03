import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.tools.refund_tools import get_order

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

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


messages = [
    {
        "role": "user",
        "content": "I want a refund for order 101"
    }
]

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=messages,
    tools=[get_order_tool],
    tool_choice="auto"
)

tool_call = response.choices[0].message.tool_calls[0]

tool_name = tool_call.function.name

arguments = tool_call.function.arguments

args = json.loads(arguments)

result = get_order(
    args["order_id"]
)


print("Tool:", tool_name)
print("Arguments:", args)
print("Result:", result)
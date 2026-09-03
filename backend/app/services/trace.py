import uuid
from datetime import datetime


class AgentTrace:

    def __init__(self, agent_name="refund_agent"):
        self.run_id = str(uuid.uuid4())
        self.agent_name = agent_name
        self.events = []

    def log_event(self, tool_name, arguments, result):

        event = {
            "event_id": len(self.events) + 1,
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "arguments": arguments,
            "result": result
        }

        self.events.append(event)

        return event

    def get_trace(self):

        return {
            "run_id": self.run_id,
            "agent_name": self.agent_name,
            "events": self.events
        }
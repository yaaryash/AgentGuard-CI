def log_event(tool_name, arguments, result):
    event = {
        "tool": tool_name,
        "arguments": arguments,
        "result": result
    }

    print("TRACE:", event)
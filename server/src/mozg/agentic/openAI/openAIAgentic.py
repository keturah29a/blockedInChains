import json
from openai import OpenAI

# Building agentic AI with OpenAI relies on combining Function Calling (Tool Use), Structured Outputs, and a loop that allows the model to reason, choose tools, and execute actions autonomously.
#
# For small to medium projects, building a native agent loop in Python using the official openai library gives you complete control without additional abstractions.

# Core Agent Architecture
#
# An AI agent typically runs in an Observation-Thought-Action loop:
#
# User Request: User provides a goal.

# LLM Decision: The model evaluates the state and decides to call a tool or return a final answer.

# Execution: Your code executes the chosen tool/function.

# Feedback: Tool results are fed back to the model as a system or tool message
# client = OpenAI()

# 1. Define tools the agent can use
def get_weather(location: str) -> str:
    # Example placeholder function
    return f"The weather in {location} is 72°F and sunny."

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name, e.g. San Francisco"}
                },
                "required": ["location"]
            }
        }
    }
]

# Map tool names to actual Python functions
available_tools = {
    "get_weather": get_weather
}

# 2. Agent Execution Loop
def run_agent(prompt: str):
    messages = [
        {"role": "system", "content": "You are a helpful agent. Use tools when needed to answer questions accurately."},
        {"role": "user", "content": prompt}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        messages.append(message)

        # Check if the model wants to call a tool
        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                # Execute function
                function_to_call = available_tools[func_name]
                result = function_to_call(**func_args)

                # Feed execution result back to the context
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        else:
            # No tool calls means the agent completed the task
            return message.content

# Run the agent
print(run_agent("What's the weather in Tokyo right now?"))
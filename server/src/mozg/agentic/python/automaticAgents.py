import os
from google import genai
from google.genai import types


#
#  A complete, lightweight implementation of an AI agent in pure Python using the official google-genai SDK.
#
#
# Key Components of an Agentic Architecture
#   Tools (Action Space): Standard Python functions decorated with docstrings. The LLM inspects the parameter types and descriptions to figure out when and how to call them.
#
#   ReAct Loop (Reason & Act): The agent decides to call get_weather("las vegas"), inspects the output (Sunny, 102°F), decides it also needs event data, calls search_events("las vegas"), and #      #   #   synthesizes the final answer.
#
#   Automatic Function Calling: Modern SDKs handle the back-and-forth orchestration automatically, executing local code when the model requests a function call until a final text answer is generated.
#
#
#

# 1. Define custom tools for the agent
def get_weather(city: str) -> str:
    """Returns the current weather forecast for a given city."""
    # In a real app, this would call an external API
    mock_data = {
        "las vegas": "Sunny, 102°F (39°C)",
        "london": "Rainy, 62°F (17°C)",
        "tokyo": "Cloudy, 78°F (26°C)",
    }
    city_clean = city.strip().lower()
    return mock_data.get(city_clean, f"Weather data not found for {city}.")


def search_events(city: str) -> str:
    """Finds upcoming outdoor events in a given city."""
    mock_events = {
        "las vegas": "Fremont Street Light Show at 9 PM; Pool Party at Caesars",
        "london": "Westminster Walking Tour at 2 PM",
    }
    city_clean = city.strip().lower()
    return mock_events.get(city_clean, f"No outdoor events found for {city}.")


# 2. Initialize the client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 3. Supply tools to the model config
config = types.GenerateContentConfig(
    tools=[get_weather, search_events],  # Pass Python functions directly
    temperature=0.0,
    system_instruction="You are an agentic travel assistant. Use your tools to gather facts before providing a plan.",
)

# 4. Use Automatic Function Calling (The Agentic Loop)
# gemini-2.5-flash natively handles tool selection, execution, and output observation
chat = client.chats.create(model="gemini-2.5-flash", config=config)

user_prompt = "I'm in Las Vegas today. Is the weather good for outdoor activities, and what events are on?"

print(f"User: {user_prompt}\n")
response = chat.send_message(user_prompt)

print(f"Agent Response:\n{response.text}")
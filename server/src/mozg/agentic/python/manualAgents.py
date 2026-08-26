import json
import os
from google import genai
from google.genai import types

# Building a manual agent loop exposes the underlying ReAct (Reason + Act) pattern. Instead of letting the 
# SDK handle execution automatically, your loop explicitly receives tool call requests from the model, executes 
# the corresponding Python functions, feeds the results back into the conversation history, and prompts the model 
# again until it produces a final text answer.
#
# What Happens Step-by-Step
#
#   disable=True: Disables the SDK's implicit execution, forcing generate_content to return FunctionCall objects inside response.function_calls.
#
#   State Management: Every interaction—user prompt, model tool call request, and tool observation result—is appended sequentially to the contents list.# 
#
#   Observation Delivery: types.Part.from_function_response wraps the local return value so Gemini can parse the tool output on the next turn.
#
#    Termination: The loop breaks automatically as soon as response.function_calls is empty, indicating the model has enough information to generate its final text response.

# 1. Define local tool functions
def get_stock_price(ticker: str) -> str:
    """Returns the current stock price for a given ticker symbol."""
    prices = {"AAPL": "$225.50", "GOOGL": "$175.20", "MSFT": "$450.10"}
    return prices.get(ticker.upper(), f"Ticker {ticker} not found.")

def convert_currency(amount: float, from_curr: str, to_curr: str) -> str:
    """Converts money between USD, EUR, and GBP."""
    rates = {("USD", "EUR"): 0.92, ("USD", "GBP"): 0.78, ("EUR", "USD"): 1.09}
    rate = rates.get((from_curr.upper(), to_curr.upper()))
    if rate:
        return f"{amount * rate:.2f} {to_curr.upper()}"
    return "Exchange rate unavailable."

# Map tool names to actual Python callables
TOOL_MAP = {
    "get_stock_price": get_stock_price,
    "convert_currency": convert_currency,
}

# 2. Configure client with automatic function calling DISABLED
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

config = types.GenerateContentConfig(
    tools=[get_stock_price, convert_currency],
    # Disable automatic execution so the model returns raw FunctionCall objects
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    temperature=0.0
)

# Maintain conversation state manually
contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(
            text="How much is 2 shares of AAPL worth in Euros?"
        )]
    )
]

# 3. The Explicit ReAct Loop
MAX_TURNS = 5
for turn in range(MAX_TURNS):
    print(f"\n--- Loop Turn {turn + 1} ---")
    
    # Step A: Send history to the model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config,
    )
    
    # Append model's response (candidate) to history
    contents.append(response.candidates[0].content)

    # Step B: Check if the model wants to call tools
    function_calls = response.function_calls
    if not function_calls:
        # No tools called -> Model produced its final text answer
        print(f"\nFinal Agent Output:\n{response.text}")
        break

    # Step C: Execute requested tools manually & construct FunctionResponse parts
    response_parts = []
    for call in function_calls:
        fn_name = call.name
        fn_args = call.args
        print(f"[Agent Action] Executing: {fn_name}({fn_args})")

        # Call local Python function
        if fn_name in TOOL_MAP:
            tool_output = TOOL_MAP[fn_name](**fn_args)
        else:
            tool_output = f"Error: Tool '{fn_name}' does not exist."

        print(f"[Tool Observation] Result: {tool_output}")

        # Package the result back into a Part.from_function_response
        response_parts.append(
            types.Part.from_function_response(
                name=fn_name,
                response={"result": tool_output}
            )
        )

    # Step D: Append function results to conversation history with role 'user'
    contents.append(
        types.Content(
            role="user",
            parts=response_parts
        )
    )
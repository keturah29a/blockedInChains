import os
from google import genai
from google.genai import types

# 1. Define custom tools (Python functions with docstrings & type hints)
def calculate_discount(price: float, discount_percent: float) -> str:
    """Calculates the final price after applying a percentage discount.
    
    Args:
        price: The original item price in dollars.
        discount_percent: The percentage discount to apply (e.g. 20 for 20%).
    """
    final_price = price * (1 - discount_percent / 100)
    return f"Original: ${price:.2f}, Final: ${final_price:.2f}"

def check_inventory(item_name: str) -> str:
    """Checks the stock level of a given product item.
    
    Args:
        item_name: The name of the product to look up.
    """
    inventory = {"laptop": 5, "phone": 0, "headphones": 12}
    stock = inventory.get(item_name.lower(), 0)
    return f"Item '{item_name}' currently has {stock} units in stock."

# Map function names to executable callables
TOOL_MAP = {
    "calculate_discount": calculate_discount,
    "check_inventory": check_inventory
}

def run_agent(user_prompt: str):
    client = genai.Client()
    
    # Define available tools for the model
    tools_config = [types.Tool(function_declarations=[
        types.FunctionDeclaration.from_callable(client=client, callable=calculate_discount),
        types.FunctionDeclaration.from_callable(client=client, callable=check_inventory),
    ])]
    
    # Initialize message memory array
    messages = [
        types.Content(role="user", parts=[types.Part.from_text(user_prompt)])
    ]
    
    print(f"Goal: {user_prompt}\n" + "-" * 50)
    
    # 2. Agentic Reasoning Loop (ReAct loop)
    max_iterations = 5
    for iteration in range(max_iterations):
        # Generate response from model with current context and tools
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(tools=tools_config)
        )
        
        # Add model output to conversation history
        candidate = response.candidates[0]
        messages.append(candidate.content)
        
        # Check if the agent requested function/tool calls
        tool_calls = response.function_calls
        if not tool_calls:
            # No tool calls means the agent completed its goal and returned a final text answer
            print("\nFinal Agent Response:\n", response.text)
            break

        # Execute requested tools and collect outputs
        tool_responses = []
        for call in tool_calls:
            print(f"[Loop {iteration + 1}] Executing tool: '{call.name}' with args {call.args}")
            
            tool_func = TOOL_MAP.get(call.name)
            if tool_func:
                result = tool_func(**call.args)
            else:
                result = f"Error: Tool '{call.name}' not found."
                
            tool_responses.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": result}
                )
            )
        
        # Feed tool execution output back into the agent's context
        messages.append(types.Content(role="user", parts=tool_responses))

# Run the agent with a compound request requiring tool usage & calculation
run_agent("Check if we have laptops in stock, and if we do, calculate what a 15% discount on a $1200 laptop would be.")


# Framework Alternatives

# While building from scratch exposes the underlying architecture, production frameworks handle memory management, standard protocols (MCP), and graph orchestration automatically:  F

# Framework     Best Used For

# LangGraph     Multi-agent collaboration, stateful graphs, and complex branching workflows.
# PydanticAI    Type-safe, production-ready agents using native Pydantic models for validation.
# CrewAIRole-based multi-agent automation systems with structured delegation.

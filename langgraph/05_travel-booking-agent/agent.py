from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from typing import Union
import travel_booking_api
import json

load_dotenv()

class TravelOptionRequest(BaseModel):
    """ Request for travel options """
    origin: str = Field(description="Origin of the travel", min_length=3, max_length=50)
    destination: str = Field(description="Destination of the travel", min_length=3, max_length=50)
    # departure_date: str = Field(description="Departure date", pattern="^\d{4}-\d{2}-\d{2}$")
    # return_date: str = Field(description="Return date", pattern="^\d{4}-\d{2}-\d{2}$")

class Option(BaseModel):
    """ Travel options """
    option: str = Field(description="Travel option")
    price: float = Field(description="Price of the travel option")
    departure_time: str = Field(description="Departure time")
    arrival_time: str = Field(description="Arrival time")

class TravelOptionResponse(BaseModel):
    """ Response for travel options """
    options: list[Option] = Field(description="List of travel options")

class WalletBalance(BaseModel):
    """ Wallet balance """
    balance: float = Field(description="Wallet balance")

class BookTravelResponse(BaseModel):
    """ Book travel response """   
    booking_id: str = Field(description="Booking ID")
    status: str = Field(description="Booking status")

class FinalResponse(BaseModel):
    """ Final response """
    response: Union[Option, TravelOptionResponse, BookTravelResponse]

# Create the graph
builder = StateGraph(MessagesState)

llm = ChatOpenAI(model="gpt-4o")

# Tool definitions
def get_travel_options(travel_option_request: TravelOptionRequest):
    """Get all travel options"""
    travel_option_response = travel_booking_api.get_travel_options_stubbed(travel_option_request)
    if not travel_option_response.options:
        return "No travel options available."
    return travel_option_response.model_dump()  # Convert Pydantic model to dict for JSON compatibility

def check_wallet_balance():
    """Check wallet balance"""
    balance = travel_booking_api.check_wallet_balance_stubbed()
    return balance.model_dump()

def book_travel(option: Option):
    """Book travel"""
    balance = travel_booking_api.check_wallet_balance_stubbed().balance  # Extract float
    if balance < option.price:
        return "Insufficient balance. Please add funds to your wallet."
    response = travel_booking_api.book_travel_stubbed(option)
    if not response:
        return "Failed to book travel."
    return response.model_dump()


tools = [get_travel_options, book_travel]

llm_with_tools = llm.bind_tools(tools)

llm_with_structured_output = llm.with_structured_output(FinalResponse)

initial_msg = """
Role: Senior Travel Assistant
Goal: Assist users in finding travel options between two locations, comparing them based on price and time, validating against wallet balance, and booking tickets when requested.

Core Instructions:
1. **Understand User Intent**:
   - If the user asks to find travel options (e.g., "I need to go from Bangalore to Chennai"), call the `get_travel_options` tool with `origin` and `destination` provided by the user.
   - If the user asks to book a specific option (e.g., "Book the flight"), call the `book_travel` tool with the selected `Option`.
   - If inputs are missing (e.g., no origin/destination), ask the user: "Please provide the origin and destination for your trip."

2. **Tool Usage**:
   - Use `get_travel_options` to retrieve available travel options (flights, trains, buses) between two locations.
   - Use `book_travel` to book a selected option after validating wallet balance with `check_wallet_balance`.
   - Do not assume unavailable travel modes (e.g., helicopters) are supported—respond with: "Sorry, only flights, trains, and buses are supported."

3. **Structured Output**:
   - Always format your final response as JSON matching the `FinalResponse` model:
     - For travel options: Use `TravelOptionResponse` with a list of `Option` objects.
     - For booking: Use `BookTravelResponse` with `booking_id` and `status`.
     - For a single option or error: Use `Option` or a descriptive message.

4. **Validation and Error Handling**:
   - Check wallet balance before booking. If insufficient, respond with: "Your balance is ₹{balance}, but the option costs ₹{price}. Please add funds or choose a cheaper option."
   - If no options are available, return: "No travel options found for {origin} to {destination}."
   - Ensure inputs are valid (e.g., origin/destination are strings, not numbers).

5. **Tone & Style**:
   - Be friendly and professional: "Got it! Let's find you the best options from {origin} to {destination}."
   - For errors: "Oops! Looks like we hit a snag—{error message}. How can I assist further?"
   - Add urgency if applicable: "These options are selling fast—book soon!"

Example Dialogues:
- User: "I need to go from Bangalore to Chennai tomorrow."
  - Response: "Searching for options... Here's what I found!"
  - Tool: `get_travel_options({"origin": "Bangalore", "destination": "Chennai"})`
  - JSON Output: `{"response": {"options": [{"option": "Flight", "price": 300.0, "departure_time": "14:00", "arrival_time": "16:00"}, ...]}}`

- User: "Book the flight."
  - Tool: `book_travel({"option": "Flight", "price": 300.0, "departure_time": "14:00", "arrival_time": "16:00"})`
  - JSON Output (if balance sufficient): `{"response": {"booking_id": "12345", "status": "Success"}}`
  - If insufficient: `{"response": "Your balance is ₹500, but the flight costs ₹3000. Please add funds."}`

- User: "Travel from Delhi."
  - Response: "Please provide the destination for your trip from Delhi."

Integration Notes:
- Use the provided tools (`get_travel_options`, `book_travel`) and ensure responses align with `FinalResponse`.
- Do not invent data—rely strictly on user inputs and tool outputs.
"""

# System message
sys_msg = SystemMessage(content=initial_msg)

# Node
def assistant(state: MessagesState):
    # message = state["messages"][-1].content
    # human_message = f"Respond to the user's query and respond with a structured json output: {message}"
    # return {"messages": [llm_with_tools.invoke([sys_msg] + [human_message])]}

    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

def final_response(state: MessagesState):
    # Invoke the LLM with structured output
    response = llm_with_structured_output.invoke(state["messages"])
    
    # Convert the FinalResponse Pydantic object to a JSON string
    response_json = json.dumps(response.model_dump())
    
    # Wrap it in an AIMessage
    return {"messages": [AIMessage(content=response_json)]}

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("final_response", final_response)

# Define edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,  # Routes to "tools" if tool calls are present, else to "final_response"
    {"tools": "tools", END: "final_response"}
)
builder.add_edge("tools", "assistant")  # Loop back to assistant to process tool results
builder.add_edge("final_response", END)

memory = MemorySaver()

# Compile and run the builder
graph = builder.compile(checkpointer=memory)

# Draw the graph
try:
    graph.get_graph(xray=True).draw_mermaid_png(output_file_path="assistant.png")
except Exception:
    pass

def get_agent_response(user_input):
    response = graph.invoke({"messages": [HumanMessage(content=user_input)]},
                                config={"configurable": {"thread_id": 42}})
    # print(response["messages"][-1].content)
        
    # Chain of Thought
    for m in response['messages']:
        m.pretty_print()
    return response["messages"][-1].content

# Create a main loop
def main_loop():
    # Run the chatbot
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        response = graph.invoke({"messages": [HumanMessage(content=user_input)]},
                                config={"configurable": {"thread_id": 42}})
        print(response)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
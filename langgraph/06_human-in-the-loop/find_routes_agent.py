from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

load_dotenv()

def find_routes(origin: str, destination: str):
    """ Tool to find the best routes for users from source to destination """
    response = [
        {
            "mode": "bus",
            "time": "30 mins",
            "cost": "$2"
        },
        {
            "mode": "train",
            "time": "20 mins",
            "cost": "$3"
        },
        {
            "mode": "cab",
            "time": "15 mins",
            "cost": "$10"
        }
    ]
    return response

# Create the graph
builder = StateGraph(MessagesState)

llm = ChatOpenAI(model="gpt-4o")

llm_with_tools = llm.bind_tools([find_routes])

initial_msg = """
    You are an AI assistant that finds the best routes for your users. Always use the find_routes tool to help users find the best routes.

    Example:
    User: I want to go from New York to Boston.
    Assistant: I found the following routes:
    - Bus: 30 mins, $2
    - Train: 20 mins, $3
    - Cab: 15 mins, $10
    Which option would you like to choose?
"""

def assistant(state: MessagesState):
    """ Agent that responds to user's queries """
    return {"messages": [llm_with_tools.invoke([SystemMessage(content=initial_msg)] + state["messages"])]}

# System message
sys_msg = SystemMessage(content=initial_msg)

memory = MemorySaver()

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode([find_routes]))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

graph = builder.compile(checkpointer=memory, name="find_routes_agent")

# Draw the graph
try:
    graph.get_graph(xray=True).draw_mermaid_png(output_file_path="find_routes_agent.png")
except Exception:
    pass

def get_agent():
    return graph

def get_agent_response(user_input):
    response = graph.invoke({"messages": [HumanMessage(content=user_input)]},
                                config={"configurable": {"thread_id": 42}})
    # print(response["messages"][-1].content)
        
    # Chain of Thought
    for m in response['messages']:
        m.pretty_print()

    return {"message": response["messages"][-1].content, "actions": []} 

# Create a main loop
def main_loop():
    # Run the chatbot
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        config={"configurable": {"thread_id": 42}}
        response = graph.invoke({"messages": [HumanMessage(content=user_input)]},
                                config=config)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
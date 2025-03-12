from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
import random

load_dotenv()

def check_balance():
    """ Tool to check the user's balance """
    return random.uniform(0, 10)

# Create the graph
builder = StateGraph(MessagesState)

llm = ChatOpenAI(model="gpt-4o")

llm_with_tools = llm.bind_tools([check_balance])

initial_msg = """
    You are an AI assistant that checks user's balance and loads fund to their account if required.
"""

def assistant(state: MessagesState):
    """ Agent that responds to user's queries """
    return {"messages": [llm_with_tools.invoke([SystemMessage(content=initial_msg)] + state["messages"])]}

# System message
sys_msg = SystemMessage(content=initial_msg)

memory = MemorySaver()

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode([check_balance]))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
builder.add_edge("assistant", END)

graph = builder.compile(checkpointer=memory, name="check_balance_agent")

# Draw the graph
try:
    graph.get_graph(xray=True).draw_mermaid_png(output_file_path="check_balance_agent.png")
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
        state = graph.get_state(config)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
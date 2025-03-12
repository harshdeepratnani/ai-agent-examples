from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
import random

load_dotenv()

def load_funds(amount: float):
    """ Tool to load funds to a user's account """
    response = f"Successfully loaded ${amount}"
    return response

# Create the graph
builder = StateGraph(MessagesState)

llm = ChatOpenAI(model="gpt-4o")

llm_with_tools = llm.bind_tools([load_funds])

initial_msg = """
    You are an AI assistant that loads fund to their account if required.
"""

def human_input(state: MessagesState):
    """ Agent that responds to user's queries """
    result = interrupt({
        "question": "Do you want me to proceed with loading funds?",
        "actions": ["Yes", "No"]
    })
    if result == 'abort':
        goto = END
        return Command(goto=goto)
    else:
        goto = "assistant"
        return Command(goto=goto)
    
def assistant(state: MessagesState):
    """ Agent that responds to user's queries """
    return {"messages": [llm_with_tools.invoke([SystemMessage(content=initial_msg)] + state["messages"])]}

# System message
sys_msg = SystemMessage(content=initial_msg)

memory = MemorySaver()

builder.add_node("human_input", human_input)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode([load_funds]))
builder.add_edge(START, "human_input")
builder.add_edge("human_input", "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
builder.add_edge("assistant", END)

graph = builder.compile(checkpointer=memory, name="load_funds_agent")

# Draw the graph
try:
    graph.get_graph(xray=True).draw_mermaid_png(output_file_path="load_funds_agent.png")
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

    graph_snapshot = graph.get_state({"configurable": {"thread_id": 42}})

    print(graph_snapshot.next)

    if graph_snapshot.next is not None and len(graph_snapshot.next) > 0 and graph_snapshot.next[0].strip() != "":
        print("Returning value1")
        return graph_snapshot.tasks[0].interrupts[0].value
    else:
        return {"message": response["messages"][-1].content, "actions": []} 

def resume_agent():
    response = graph.invoke(Command(resume="Yes resume"), config={"configurable": {"thread_id": 42}})
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

        print("Resuming agent workflow")

        response = graph.invoke(Command(resume="Yes resume"), config=config)

        state = graph.get_state(config)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
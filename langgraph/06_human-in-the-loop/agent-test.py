from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

load_dotenv()

# Create the graph
builder = StateGraph(MessagesState)

llm = ChatOpenAI(model="gpt-3.5-turbo")

initial_msg = "You are a helpful assistant."

# System message
sys_msg = SystemMessage(content=initial_msg)

# Node
def step1(state: MessagesState):
    
    print("Inside step1")

    return {"messages": "Inside step1"}

def step2(state: MessagesState):
    
    print("Inside step2")

    print("---human_feedback---")
    feedback = interrupt({
        "message": "Want to resume?",
        "actions": ["Yes resume", "No resume"]
    })

    return {"messages": feedback}

def step3(state: MessagesState):
    
    print("Inside step3")

    return {"messages": "Inside step3"}

# Define nodes: these do the work
builder.add_node("step1", step1)
builder.add_node("step2", step2)
builder.add_node("step3", step3)

# Define edges
builder.add_edge(START, "step1")
builder.add_edge("step1", "step2")
builder.add_edge("step2", "step3")  # Loop back to assistant to process tool results
builder.add_edge("step3", END)

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

    graph_snapshot = graph.get_state({"configurable": {"thread_id": 42}})
    print(graph_snapshot)
    print(graph_snapshot.next)
    print(graph_snapshot.tasks[0].interrupts[0].value)

    if graph_snapshot.next != None:
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
        print("state start")
        print(state)
        print(state.next)
        print(state.tasks[0].interrupts[0].value)
        print("state end")
        print(response)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

        print("Resuming agent workflow")

        response = graph.invoke(Command(resume="Yes resume"), config=config)

        state = graph.get_state(config)
        print("state start")
        print(state)
        print(state.next)
        print(state.tasks[0].interrupts[0].value)
        print("state end")
        print(response)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
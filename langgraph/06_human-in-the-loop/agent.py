from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import MessagesState
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
import find_routes_agent, cab_booking_agent, load_funds_agent, check_balance_agent

load_dotenv()

# Create the graph
builder = StateGraph(MessagesState)

llm = ChatOpenAI(model="gpt-4o")

initial_msg = """You are the Supervisor Agent in an Itinerary Planner application. Your role is to coordinate and oversee the workflow of three specialized agents to 
                help users plan and book travel from an origin to a destination.
                ### Your Responsibilities:
                Coordinate Agents**: Manage the flow between:
                - Route Finder Agent**: Finds the best travel options (bus, train, or cab) from origin to destination.
                - Cab Booking Agent**: Books a cab if selected by the user.
                - Check Balance Agent**: Checks the user's public transit card balance.
                - Load Funds Agent**: Loads funds if needed for bus or train options.
   """

# System message
sys_msg = SystemMessage(content=initial_msg)

find_routes_agent = find_routes_agent.get_agent()
cab_booking_agent = cab_booking_agent.get_agent()
check_balance_agent = check_balance_agent.get_agent()
load_funds_agent = load_funds_agent.get_agent()

supervisor = create_supervisor([find_routes_agent, cab_booking_agent, check_balance_agent, load_funds_agent], model = llm, prompt = sys_msg, output_mode="full_history")

memory = MemorySaver()

# Compile and run the builder
agent = supervisor.compile(checkpointer=memory)

# Draw the graph
try:
    agent.get_graph(xray=True).draw_mermaid_png(output_file_path="agent.png")
except Exception:
    pass

def get_agent_response(user_input):
    response = agent.invoke({"messages": [HumanMessage(content=user_input)]},
                                config={"configurable": {"thread_id": 42}})
    # print(response["messages"][-1].content)
        
    # Chain of Thought
    for m in response['messages']:
        m.pretty_print()

    graph_snapshot = agent.get_state({"configurable": {"thread_id": 42}})

    print(graph_snapshot.next)

    if graph_snapshot.next is not None and len(graph_snapshot.next) > 0 and graph_snapshot.next[0].strip() != "":
        print("Returning value1")
        return graph_snapshot.tasks[0].interrupts[0].value
    else:
        return {"message": response["messages"][-1].content, "actions": []} 

def resume_agent(user_input):
    print(f"User input: {user_input}")
    response = agent.invoke(Command(resume=user_input), config={"configurable": {"thread_id": 42}})
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
        response = agent.invoke({"messages": [HumanMessage(content=user_input)]},
                                config=config)
        state = agent.get_state(config)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

        print("Resuming agent workflow")

        response = agent.invoke(Command(resume="Yes resume"), config=config)

        state = agent.get_state(config)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
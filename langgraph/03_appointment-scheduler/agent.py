from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
import schedule_appointment
import retriever

load_dotenv()

def appointment_scheduler(message: str):
    """ Tool to schedule customer's appointment """
    meeting_url = schedule_appointment.get_meeting_url()
    return {"messages": f"Schedule an appointment here: {meeting_url}"}

def faq_lookup(message: str):
    """ Tool that lookup answers to the FAQs """
    answer = retriever.get_answer(message)
    return {"messages": answer}

tools = [faq_lookup, appointment_scheduler]
llm = ChatOpenAI(model="gpt-3.5-turbo")

llm_with_tools = llm.bind_tools(tools)

def assistant(state: MessagesState):
    """ Agent that responds to user's queries """

    initial_msg = """ You are a helpful assistant. Your primary responsibility is to assist SwiftLife Insurance customers with 
    their queries. You must always greet the customers. You may refer the FAQs or provide users with a meeting link in case if user 
    wants to schedule a meeting. """

    # System message
    system_message = SystemMessage(content=initial_msg)

    return {"messages": [llm_with_tools.invoke([system_message] + state["messages"])]}

# Initialize memory to persist state between graph runs
checkpointer = MemorySaver()

# Create the graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile and run the builder
graph = builder.compile(checkpointer=checkpointer)

# Draw the graph
try:
    graph.get_graph(xray=True).draw_mermaid_png(output_file_path="assistant.png")
except Exception:
    pass

def get_agent_response(user_input):
    response = graph.invoke({"messages": [HumanMessage(content=user_input)]},
                                config={"configurable": {"thread_id": 42}})
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
        print(response["messages"][-1].content)
        
        # Chain of Thought
        # for m in response['messages']:
        #     m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()

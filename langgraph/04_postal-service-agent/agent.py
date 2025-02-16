import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import retriever
import postal_service_api

load_dotenv()

# Create the graph
builder = StateGraph(MessagesState)

llm = ChatOpenAI(model="gpt-3.5-turbo")

def faq_lookup(message: str):
    """ Tool that lookup answers to the FAQs """

    answer = retriever.get_answer(message)
    return {"messages": answer}

def create_mailing_order(recipient: str, address: str, package_type: str):
    """ Create a mailing order """
        
    status, message, tracking_number = postal_service_api.create_mailing_order_stubbed(recipient, address, package_type) # stubbed api call
    return status, message, tracking_number

def create_shipment_order(recipient: str, address: str, package_type: str):
    """ Create a shipment order """

    status, message, tracking_number = postal_service_api.create_shipment_order_stubbed(recipient, address, package_type) # stubbed api call
    return status, message, tracking_number


def get_api_specs(order_category: str):
    """ Get API Specifications for Mailing or Shipment Order. The order creation request should honor these request specifications in order to successfully create an order. """

    return postal_service_api.get_api_specs_stubbed() # stubbed api call

def validate_order(recipient: str, address: str, package_type: str):
    """ Determine if the order creation request is valid by checking if all required values have been supplied """

    return postal_service_api.validate_order_stubbed(recipient, address, package_type) # stubbed api call

tools = [faq_lookup, validate_order, get_api_specs, create_shipment_order, create_mailing_order]

llm_with_tools = llm.bind_tools(tools)

initial_msg = """
   You are a helpful assistant. Your primary responsibility is to assist in creating mail and shipment orders. 
   You may use any of the available tools if necessary to execute your tasks, otherwise there no need to use any tool. 
   Pre-requisites for creating mailing order:
   1. Get the latest api specifications.
   2. Validate if all the required information has been supplied.
   
   DO NOT ASSUME ANY INFORMATION WHICH HAS NOT BEEN SUPPLIED AS AN INPUT. IF REQUIRED INPUT IS MISSING, THSN ASK USER FOR INPUT.
"""

# System message
sys_msg = SystemMessage(content=initial_msg)

# Node
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

memory = MemorySaver()

# Compile and run the builder
graph = builder.compile(checkpointer=memory)

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
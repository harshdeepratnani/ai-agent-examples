from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import create_react_agent
import json

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

store = InMemoryStore(
    index={"embed": "openai:text-embedding-3-small"}
)

class State(TypedDict):
    '''
    Define the state of the agent.
    '''
    messages: Annotated[list, add_messages]
    triage_result: str

manage_memory_tool = create_manage_memory_tool(
    namespace=(
        "semantic_memory", 
        "{langgraph_user_id}",
        "collection"
    )
)
search_memory_tool = create_search_memory_tool(
    namespace=(
        "semantic_memory",
        "{langgraph_user_id}",
        "collection"
    )
)

tools = [manage_memory_tool, search_memory_tool]

llm_with_tools = llm.bind_tools(tools)

responses = {
    "overheating_response": "Check if vents are clear, place it on a hard surface, and update drivers. If it persists, contact support for repair options.",
    "returns_response": "Returns are accepted within 30 days with a receipt. Log into your account, go to 'Orders,' and select 'Return Item.' Ship it back with the provided label.",
    "charging_response": "Try a different cable and charger. Clean the charging port with a small brush. If it still fails, it may need repair—contact us.",
    "smartwatch_response": "Go to Settings > System > Reset Options > Factory Reset. Ensure it's charged first."
    }

response_agent_system_prompt = ""

response_agent_system_prompt_template = """
You are a customer support agent for TechGadget Store, specializing in tech products like laptops, phones, and smart devices. Use the following FAQs to assist users, and adapt based on the conversation history. If unsure, provide a helpful general response and offer to escalate.

<Instructions>
{instructions}
</Instructions>

< Tools >
You have access to the following tools to help manage communications:

1. manage_memory_tool - Store any relevant information about customer, their electronic devices, complaints etc. in memory for future reference
2. search_memory_tool - Search for any relevant information that may have been stored in memory
</ Tools >

< Few shot examples >

Here are some examples of previous emails, and how they should be handled.
Follow these examples more than any instructions above

{examples}
</ Few shot examples >

### Guidelines
- Be friendly, concise, and professional.
- IMPORTANT: Always use available memory tools to search and manage information.
- Use the conversation history to avoid repeating questions or steps.
- If the user's issue isn't in the FAQs, suggest contacting support with their order number.
"""

memory = MemorySaver()

def add_example_for_episodic_memory():
    """
    Add example for episodic memory.
    """
    namespace = (
        "episodic_memory",
        "Harshdeep",
        "examples"
    )
    
    store.put(
        namespace, 
        "examples", 
        {"example": responses["overheating_response"]}
    )

def triage_agent(state: State):
    '''
    Triage agent to handle user queries.
    '''

    trigate_agent_system_prompt = """
    You are a triage agent for TechGadget Store, specializing in tech products like laptops, phones, and 
    smart devices. Your task is to classify user queries into one of the following categories: 
    overheating, returns, charging, or smartwatch.
    """
    
    messages = [SystemMessage(content=trigate_agent_system_prompt)] + state["messages"]

    add_example_for_episodic_memory()

    response = llm.invoke(messages)

    print("Triage Result:", response)

    return {"triage_result": response}

def create_response_agent_prompt(state: State, config):
    """
    Create a prompt for the response agent based on the triage result.
    """
    print("State:", state)
    triage_result = state["triage_result"].content
    print("Triage Result:", triage_result)
    langgraph_user_id = config['configurable']['langgraph_user_id']
    namespace = (langgraph_user_id, )

    # Procedural Memory Implementation
    if triage_result == "overheating":
        instructions_from_memory = store.get(namespace, "overheating")
        if instructions_from_memory is None:
            instructions = responses["overheating_response"]
            store.put(
                namespace, 
                "overheating", 
                {"prompt": responses["overheating_response"]}
            )
        else:
            instructions = instructions_from_memory.value["prompt"]
    elif triage_result == "returns":
        instructions_from_memory = store.get(namespace, "returns")
        if instructions_from_memory is None:
            instructions = responses["returns_response"]
            store.put(
                namespace, 
                "returns", 
                {"prompt": responses["returns_response"]}
            )
        else:
            instructions = instructions_from_memory.value["prompt"]
    elif triage_result == "charging":
        instructions_from_memory = store.get(namespace, "charging")
        if instructions_from_memory is None:
            instructions = responses["charging_response"]
            store.put(
                namespace, 
                "charging", 
                {"prompt": responses["charging_response"]}
            )
        else:
            instructions = instructions_from_memory.value["prompt"]
    elif triage_result == "smartwatch":
        instructions_from_memory = store.get(namespace, "smartwatch")
        if instructions_from_memory is None:
            instructions = responses["smartwatch_response"]
            store.put(
                namespace, 
                "smartwatch", 
                {"prompt": responses["smartwatch_response"]}
            )
        else:
            instructions = instructions_from_memory.value["prompt"]
    else:
        instructions = "I don't have a response for that."
    
    # Episodic Memory Implementation
    namespace = (
        "episodic_memory",
        config['configurable']['langgraph_user_id'],
        "examples"
    )
    
    examples = store.search(
        namespace, 
        query=str({"example": state['messages'][-1].content}),
    )

    examples=format_few_shot_examples(examples)

    print("Examples:", examples)
    print("Instructions:", instructions)

    response_agent_system_prompt = response_agent_system_prompt_template.format(instructions=instructions,
                                                                                   examples=examples)
    return [SystemMessage(content=response_agent_system_prompt)] + state["messages"]

# Format list of few shots
def format_few_shot_examples(examples):
    strs = ["Here are some previous examples:"]
    for eg in examples:
        strs.append(eg.value["example"])
    return "\n\n------------\n\n".join(strs)

def assistant(state: State, config):
    """
    Response agent to handle user queries.
    """
    user_input = state["messages"][-1].content
    assistant_system_prompt = create_response_agent_prompt(state, config)
    assistant_prompt = assistant_system_prompt + [HumanMessage(content=user_input)]
    response = llm_with_tools.invoke(assistant_prompt)
    return {"messages": response}

# response_agent = create_react_agent(llm, tools, prompt=create_response_agent_prompt, 
#                                     checkpointer=memory, store=store)

react_builder = StateGraph(State)

react_builder.add_node("assistant", assistant)
react_builder.add_node("tools", ToolNode(tools))

react_builder.add_edge(START, "assistant")
react_builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
react_builder.add_edge("tools", "assistant")

response_agent = react_builder.compile(checkpointer=memory, store=store)

# Create the graph
builder = StateGraph(State)

builder.add_node("triage_agent", triage_agent)
builder.add_node("response_agent", response_agent)

builder.add_edge(START, "triage_agent")
builder.add_edge("triage_agent", "response_agent")
builder.add_edge("response_agent", END)

app = builder.compile(checkpointer=memory, store=store)

# Draw the graph
try:
    app.get_graph(xray=True).draw_mermaid_png(output_file_path="assistant.png")
except Exception:
    pass

def get_agent_response(user_input):
    thread_id = 42
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {"messages": user_input}

    response = app.invoke(initial_state, config=config)
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

        thread_id = 42
        config = {"configurable": {"thread_id": thread_id,
                                   "langgraph_user_id": "Harshdeep"}}

        initial_state = {"messages": user_input}

        response = app.invoke(initial_state, config=config)
        # print(response["messages"][-1].content)
        # print(response)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
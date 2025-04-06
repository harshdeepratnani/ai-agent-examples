from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
import json

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

def greet_user():
    '''
    Greet the user when they start the conversation.
    '''
    print("Welcome to the TechGadget Store customer support chatbot. How can I help you today?")

tools = [greet_user]

initial_msg = """
You are a customer support agent for TechGadget Store, specializing in tech products like laptops, phones, and smart devices. Use the following FAQs to assist users, and adapt based on the conversation history. If unsure, provide a helpful general response and offer to escalate.

### FAQs
1. **My laptop is overheating. What should I do?**
   - Check if vents are clear, place it on a hard surface, and update drivers. If it persists, contact support for repair options.

2. **How do I return a product?**
   - Returns are accepted within 30 days with a receipt. Log into your account, go to "Orders," and select "Return Item." Ship it back with the provided label.

3. **My phone won't charge. Help!**
   - Try a different cable and charger. Clean the charging port with a small brush. If it still fails, it may need repair—contact us.

4. **How do I reset my smartwatch?**
   - Go to Settings > System > Reset Options > Factory Reset. Ensure it's charged first.

### Guidelines
- Be friendly, concise, and professional.
- Use the conversation history to avoid repeating questions or steps.
- If the user's issue isn't in the FAQs, suggest contacting support with their order number.
"""

# Set up SQLite checkpointing
conn = sqlite3.connect("memory.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

agent = create_react_agent(llm, tools, prompt=initial_msg, checkpointer=memory)

# Draw the graph
try:
    agent.get_graph(xray=True).draw_mermaid_png(output_file_path="assistant.png")
except Exception:
    pass

def get_agent_response(user_input):
    thread_id = 42
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {"messages": user_input}

    response = agent.invoke(initial_state, config=config)
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
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {"messages": user_input}

        response = agent.invoke(initial_state, config=config)
        # print(response["messages"][-1].content)
        # print(response)
        
        # Chain of Thought
        for m in response['messages']:
            m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()
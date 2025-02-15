from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")

# Initialize Tavily
tavily = TavilySearchResults(max_results=3)

tools = [tavily]

# Initialize memory to persist state between graph runs
checkpointer = MemorySaver()

app = create_react_agent(llm, tools, checkpointer=checkpointer)

system_message = """ You are a helpful assistant. Your primaty responsibility is to compare prices of the items as per user's ask.
Limit your search to walmart.ca, loblaws.ca and realcanadiansuperstore.ca. 
Do not compare outside of these stores anywhere else, even if the prices are cheaper.
Respond with a table output with price of the item in all three stores. Make sure that the prices are always calculated as per pound.

Example:

| Store           | Walmart     | Loblaws       | Real Canadian |
|-----------------|-------------|---------------|---------------|
| Milk            | $3.29 / lb  | $3.25 / lb    | $3.30 / lb    |


Do your best!
"""

# Create a main loop
def main_loop():
    # Run the chatbot
    while True:
        user_input = input(">> ") # Example: "What is the price of royal gala apples today?"
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        messages = [SystemMessage(content=system_message)] + [HumanMessage(content=user_input)]
        response = app.invoke({"messages": messages},
                                config={"configurable": {"thread_id": 42}})
        print(response["messages"][-1].content)
        
        # Chain of Thought
        # for m in response['messages']:
        #     m.pretty_print()

# Run the main loop
if __name__ == "__main__":
    main_loop()

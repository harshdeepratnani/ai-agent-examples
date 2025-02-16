from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")

system_message = "You are a helpful assistant."

# Create a main loop
def main_loop():
    # Run the chatbot
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        messages = [SystemMessage(content=system_message)] + [HumanMessage(content=user_input)]
        response = llm.invoke(messages)
        print(response.content)

# Run the main loop
if __name__ == "__main__":
    main_loop()

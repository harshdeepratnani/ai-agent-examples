### **Hello World: AI Agent with GPT-3.5-Turbo**  

This is a simple **Hello World** example demonstrating how to use **GPT-3.5-Turbo** as an AI agent to respond to user queries. It runs a basic chatbot where the model acts as a helpful assistant.  

---

## 🚀 **Setup Instructions**  

### **1️⃣ Prerequisites**  
- Python 3.8+ installed  
- An **OpenAI API Key** (Get it from [OpenAI](https://platform.openai.com/signup/))  

### **2️⃣ Install Dependencies**  
First, install the required package:  

```bash
pip install langchain openai python-dotenv
```

### **3️⃣ Set Up Your OpenAI API Key**  
Create a `.env` file in the project directory and add:  

```bash
OPENAI_API_KEY=your_api_key_here
```

Alternatively, you can set it as an environment variable in your terminal:  

```bash
export OPENAI_API_KEY="your_api_key_here"
```

---

## 📜 **Usage**  
Run the script:  

```bash
python hello_world.py
```

It will prompt for user input. Type a question, and the AI will respond.  

💡 **To exit, type:** `quit`, `exit`, or `q`.  

Example interaction:  

```
>> What is LangChain?
LangChain is a framework for building applications powered by LLMs, providing tools for prompt management, memory, and agent-based interactions.
```

---

## 🔍 **How It Works**  
1️⃣ Loads the **GPT-3.5-Turbo** model using `langchain_openai.ChatOpenAI`.  
2️⃣ Defines a **system message** to set the AI’s behavior.  
3️⃣ Runs an interactive loop where the user inputs a query.  
4️⃣ The AI **processes the message** and responds.  
5️⃣ The loop continues until the user types `quit`, `exit`, or `q`.  

---

## 🛠 **Next Steps**  
This is a minimal example to get started. You can extend it by:  
✅ Connecting external tools like **web search**  
✅ Using memory to retain past conversations  
✅ Deploying as a web or chat app  

---

## 📌 **Resources to Learn More**
- [OpenAI API](https://platform.openai.com/docs/)

---
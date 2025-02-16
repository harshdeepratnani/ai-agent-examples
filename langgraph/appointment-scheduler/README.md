# 📅 RAG + Appointment Scheduler AI Agent  

This is an **AI-powered Appointment Scheduler** for **SwiftLife Insurance Company**.  
The agent can:  
✅ Answer policy-related questions using **RAG (Retrieval-Augmented Generation)**.  
✅ Schedule appointments via **Calendly’s API**.  

## 🛠️ Tech Stack  
- **LangGraph** – Multi-agent workflow  
- **OpenAI’s GPT-3.5 Turbo** – LLM for natural language understanding  
- **ChromaDB** – Vector store for document retrieval  
- **Calendly API** – Appointment scheduling  

## 🔍 How It Works  
1. The **user asks a question** → The agent **checks the policy document** using **RAG**.  
2. If a **match is found**, the agent retrieves and responds.  
3. If the user **wants to book an appointment**, the agent calls **Calendly’s API** and provides confirmation.  

## 🚀 Getting Started  

### **1️⃣ Install Dependencies**  
```bash
pip install -r requirements.txt
```
### 2️⃣ Set Up Environment Variables
Copy .env.example and rename it to .env, then fill in your API keys:
```bash
LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
OPENAI_API_KEY=
CALENDLY_API_KEY=
```

### 3️⃣ Run the AI Agent
```bash
python agent.py
```

### 💡 Example Queries & Agent Behavior

| User Query | Expected Response | Action Taken |
|------------|-------------------|--------------|
| Hi! My name is Harsh	| Hello, Harsh! How can I assist you today? | No tool calls |
| What is the eligibility criteria? |	Eligibility: Age 18-65, medical check required. |	Uses RAG |
| What is Term Life Insurance? |	Term Life provides coverage for a fixed period. |	Uses RAG |
| I would like to schedule an appointment. |	Sure! Let me provide you a link to choose your time slot... | Calls Calendly API

### 📸 LangGraph Visual Representation
(Refer to assistant.png for the AI agent’s workflow diagram.)
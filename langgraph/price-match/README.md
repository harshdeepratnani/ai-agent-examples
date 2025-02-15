# Price Match Agent using LangGraph & Tavily

This repository contains a simple **Price Match Agent** built using [LangGraph](https://github.com/langchain-ai/langgraph) and [Tavily](https://tavily.com/). The agent fetches the prices of a user-specified product from **Walmart, Loblaws, and Real Canadian Superstore** and returns a table summarizing the prices.

## Features
- Uses **LangGraph** to manage the workflow of querying multiple sources.
- Uses **Tavily** for web search to fetch real-time pricing.
- Outputs a formatted table with product prices from different stores.

## Installation
### Prerequisites
Ensure you have Python 3.8+ installed on your system.

### Steps
1. Clone this repository:
   ```sh
   git clone https://github.com/harshdeepratnani/price-match.git
   cd price-match
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up your Tavily API key:
   ```sh
   export TAVILY_API_KEY=your_api_key_here  # For Linux/macOS
   set TAVILY_API_KEY=your_api_key_here  # For Windows (cmd)
   ```
   Alternatively, you can store the API key in an `.env` file:
   ```sh
   echo "TAVILY_API_KEY=your_api_key_here" > .env
   ```

## Usage
Run the script and enter a product name when prompted:
```sh
python agent.py

Sample user input: >>"What is the price of royal gala apples today?"
```
The agent will return a table displaying prices from Walmart, Loblaws, and Real Canadian Superstore.

### Example Output
```
| Store             | Walmart     | Loblaws       | Real Canadian |
|-------------------|-------------|---------------|---------------|
| Royal Gala Apples | $3.29 / lb  | $3.25 / lb    | $3.30 / lb    |
```

---

## 📌 **Resources to Learn More**
- [LangChain Docs](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Tavily Web Search API](https://tavily.com/)

---

**Happy price matching! 🎯**
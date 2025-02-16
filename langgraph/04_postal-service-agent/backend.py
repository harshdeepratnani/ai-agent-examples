# expose an endpoint for Whatsapp

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from langgraph_sdk import get_client
from langchain_core.messages import convert_to_messages, HumanMessage
import time
from typing import Optional
from agent import get_agent_response  # Import AI agent function

app = FastAPI()

@app.post("/process")
async def process_request(user_input):
    try:
        result = await get_agent_response(user_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
# expose an endpoint for Whatsapp

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_core.messages import convert_to_messages, HumanMessage
from agent import get_agent_response  # Import AI agent function

app = FastAPI()

# Request payload model
class UserInputRequest(BaseModel):
    user_input: str

@app.post("/process")
def process_request(request: UserInputRequest):
    try:
        result = get_agent_response(request.user_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
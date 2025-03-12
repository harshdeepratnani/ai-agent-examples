from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent import get_agent_response, resume_agent

app = FastAPI()

class UserInput(BaseModel):
    user_input: str

@app.post("/get_response")
async def get_agent_response_endpoint(user_input: UserInput):
    response = get_agent_response(user_input.user_input)
    return JSONResponse(content=response)

@app.post("/resume")
async def resume_agent_endpoint(user_input: UserInput):
    response = resume_agent(user_input.user_input)
    return JSONResponse(content=response)
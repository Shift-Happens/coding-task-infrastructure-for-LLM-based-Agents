from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import Dict, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import asyncio
from contextlib import asynccontextmanager

class Message(BaseModel):
    msg: str
    session_id: Optional[str] = None

class Response(BaseModel):
    msg: str
    session_id: str

settings = Settings()
app = FastAPI()
sessions: Dict[str, EnhancedMemory] = {}

def create_agent(memory: Optional[EnhancedMemory] = None):
    llm = ChatOpenAI(
        model_name=settings.MODEL_NAME,
        temperature=0
    )
    
    tools = [FileSystemTool()]
    
    system_prompt = """You are an advanced file system operator with memory of past interactions.
    Work step by step, always verify operations before executing them.
    Use the provided tools instead of raw shell commands for safety.
    Explain your reasoning before taking actions."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory.memory if memory else None,
        verbose=settings.DEBUG
    )

@app.post("/agent")
async def process_agent_request(message: Message) -> Response:
    session_id = message.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = EnhancedMemory(
            session_id=session_id,
            redis_url=settings.REDIS_URL
        )
    
    memory = sessions[session_id]
    agent_executor = create_agent(memory)
    
    try:
        response = await agent_executor.ainvoke({"input": message.msg})
        memory.add_message("user", message.msg)
        memory.add_message("assistant", response["output"])
        
        return Response(
            msg=str(response["output"]),
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

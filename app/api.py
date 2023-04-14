"""LLMitlessAPI
"""
from uuid import uuid4
from typing import Dict

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent import agent_loop


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    """
    """
    service: str
    data: str


tasks_status: Dict[str, str] = {}


@app.post('/a')
async def trigger_new_task(
    body: RequestBody,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    new_task_id = str(uuid4())
    background_tasks.add_task(
        agent_loop,
        task_id=new_task_id,
        tasks_status=tasks_status,
        service=body.service,
        data=body.data
    )
    tasks_status[new_task_id] = "running"
    return {"task_id": new_task_id}


@app.get("/{task_id}")
async def check_task(task_id: str) -> Dict[str, str]:
    if task_id in tasks_status:
        status = tasks_status[task_id]
    else:
        status = "not found"
    return {"result": status}
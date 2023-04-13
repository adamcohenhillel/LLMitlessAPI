"""
"""
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from pipelines import process_project



demo_router = APIRouter()


class ProcessProject(BaseModel):
    path: str



@demo_router.post('/')
async def demo_process(
    body: ProcessProject,
    background_tasks: BackgroundTasks,
):
    """Demo route

    :param body: request body.
    :param background_tasks: background tasks.
    """
    background_tasks.add_task(
        process_project,
        body.path,
    )
    return "Started processing project."


@demo_router.get('/')
async def get():
    """Demo GET route
    """
    return "heo"
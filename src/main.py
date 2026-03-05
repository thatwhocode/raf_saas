from fastapi import FastAPI
from src.schemas import PromptRequest, TaskData
from src.worker import generate_text_task, celery_app
from celery.result import AsyncResult

app = FastAPI()

@app.post("/generate", response_model= TaskData)
async def generate_task_id(user_prompt : PromptRequest):
    task = generate_text_task.delay(user_prompt.prompt)
    return TaskData(task_id=task.id)
@app.get("/status/{task_id}")
async def task_status_getter(task_id : str):
    result = AsyncResult(task_id, app=celery_app)
    return {
    "status": result.status, 
    "result": result.result if result.status == "SUCCESS" else None
}
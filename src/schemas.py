from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt : str

class TaskData(BaseModel):
    task_id : str
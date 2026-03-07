from fastapi import APIRouter, UploadFile, File, Depends
from worker import celery_app
from src.core.dependencies import RagServiceFactory, RagService
from src.api.schemas import TaskData, PromptRequest, UserRequest
import os
import shutil
from celery.result import AsyncResult
from src.worker import process_document_task
from src.worker import generate_text_task
from src.api.deps import oauth2_scheme, Dependencies
rag_factory = RagServiceFactory(
    qdrant_url="http://qdrant:6333", 
    ollama_host="http://ollama:11434",
    embed_model="nomic-embed-text",
    chat_model="llama3"
)
router = APIRouter()
UPLOAD_PATH : str  = "app/files"
@router.post("/generate", response_model= TaskData)
async def generate_task_id(user_prompt : PromptRequest):
    task = generate_text_task.delay(user_prompt.prompt)
    return TaskData(task_id=task.id)
@router.get("/status/{task_id}")
async def task_status_getter(task_id : str):
    result = AsyncResult(task_id, app=celery_app)
    return {
    "status": result.status, 
    "result": result.result if result.status == "SUCCESS" else None
}
@router.post("/file")
async def upload_file(file : UploadFile=File(...), token: str = Depends(oauth2_scheme), deps: Dependencies = Depends()):
    current_user = await deps.auth_service.get_user_from_token(token)
    
    os.makedirs(UPLOAD_PATH, exist_ok = True)
    file_path  = os.path.join(UPLOAD_PATH, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    

    task = process_document_task.delay(file_path, str(current_user.id))

    return{
        "file": file.filename,
        "task_id": task.id,
        "message": "File recieved and sent to backgrouund processing"
    }
@router.post("/rag_chat")
async def chat_with_rag(data: UserRequest, token : str = Depends(oauth2_scheme), service: RagService = Depends(rag_factory), deps : Dependencies = Depends()):
    current_user = await deps.auth_service.get_user_from_token(token)
    answer = await service.chat_request(question=data.query, user_id=current_user.id, system_prompt=data.system_prompt)
    return {"answer": answer}
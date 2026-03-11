from celery import Celery
from shared_packages.core.config import RedisSettings
from ollama import AsyncClient
from qdrant_client import AsyncQdrantClient
from adapters.qdrant_adapter import VectorStoreAdapter
from adapters.ollama_adapter import LLMAdapter
from shared_packages.core.config import QdrantSettings, LLMSettings
import asyncio
from uuid import UUID
qdrrant_settings = QdrantSettings()
ollama_settings = LLMSettings()
ollama_client= AsyncClient(host=f"{ollama_settings.OLLAMA_URL}")
qdrant_client = AsyncQdrantClient(url=f"{QdrantSettings.QDRANT_URL}")
        
redis= RedisSettings()
celery_app = Celery('hello', broker=redis.REDIS_URL, backend=redis.REDIS_URL)

@celery_app.task(name='generate_text_task')
def generate_text_task(prompt_text: str):
    async def chat():
        response =  await ollama_client.chat(model='llama3', messages=[])
        {
        'role': 'user',
        'content': f"{prompt_text}"
        },
        return response.message.content
    result_message = asyncio.run(chat())
    return result_message
@celery_app.task(bind=True, name='process_document_task')
def process_document_task(self, file_path: str, user_id_str: str):
    try:
        user_id = UUID(user_id_str)
        
        async def run_ingestion():
            from src.services.ingestor import IngestionService
            
            ingestion = IngestionService(VectorStoreAdapter(qdrant_client, qdrrant_settings.QDRANT_COLLECTION), LLMAdapter(ollama_client, "nomic-embed-text", "llama3" ))
            await ingestion.process_and_save_document(file_path, user_id)
            return f"Документ {file_path} успішно оброблено"

        result_message = asyncio.run(run_ingestion())
        return {"status": "success", "message": result_message}
        
    except Exception as e:
        # Тут ми зловимо помилку, якщо щось піде не так
        return {"status": "error", "detail": str(e)}
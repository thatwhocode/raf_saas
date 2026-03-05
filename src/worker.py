from celery import Celery
from shared_packages.core.config import RedisSettings
from ollama import Client

redis= RedisSettings()
celery_app = Celery('hello', broker=redis.REDIS_URL, backend=redis.REDIS_URL)
client  = Client(
    host="http://ollama:11434",
    headers = {'x-some-header' : 'some-value'}
)

@celery_app.task
def generate_text_task(prompt_text: str):
    response = client.chat(model='llama3', messages=[
        {
        'role': 'user',
        'content': f"{prompt_text}"
        },
    ])
    return response.message.content
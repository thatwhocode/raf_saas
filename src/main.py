from fastapi import APIRouter, FastAPI
from api.routes import router
from src.auth.auth import auth_router
from contextlib import asynccontextmanager
from src.api.routes import rag_factory
@asynccontextmanager
async def lifespan(app: FastAPI):

    service = rag_factory()
    await service.vector_store.ensure_collection_exists()
    yield


api_version_prefix = "v1"
app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix=f"/{api_version_prefix}/auth", tags=["Auth"])

app.include_router(router, prefix="/LLM", tags=["LLM"])


    
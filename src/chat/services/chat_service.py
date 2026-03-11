from src.chat.repositories.chat_repo import ChatRepository
from src.chat.repositories.access_repo import AccessRepository
from src.chat.repositories.message_repo import MessageRepository
from sqlalchemy.ext.asyncio import AsyncSession

import uuid
class ChatService():
    def __init__(self,session : AsyncSession, chat_repo : ChatRepository, access_repo : AccessRepository, message_repo : MessageRepository):
        self.chat_repo = chat_repo
        self.access_repo = access_repo
        self.message_repo = message_repo
        self.session = session # на майбутнє щоб комітити в сервісі
    async def initiate_new_chat(self, user_id : uuid.UUID ):
        return await self.chat_repo.create_chat(user_id=user_id)
    async def get_chat_context(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        if not await self.access_repo.is_user_in_chat(user_id=user_id, chat_id=chat_id):
            raise AccessDeniedException
        history = await self.message_repo.get_history(chat_id)
        formatted_history = [
        {"role": m.role.value.lower(), "content": m.content} for m in history]
        system_prompt = {
        "role": "system", 
        "content": """ou are a highly capable AI Assistant operating through a secure hybrid-cloud bridge on a local NVIDIA RTX 3080 GPU.

            Core Directives:

                Privacy First: All inference is performed locally. Emphasize that no user data is sent to third-party cloud LLM providers.

                Technical Excellence: Your responses should be concise, professional, and accurate.

                Context Awareness: You have access to the conversation history. Use it to provide relevant and coherent follow-up answers.

                Identity: If asked, acknowledge that you are part of a custom-built private AI infrastructure designed for data sovereignty.

            Maintain a helpful yet brief tone. Avoid unnecessary verbosity"""
                        }
        return [system_prompt] + formatted_history
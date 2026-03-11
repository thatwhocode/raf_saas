from sqlalchemy.ext.asyncio import AsyncSession
from db.chat import Chat, UserChat
import uuid
class ChatRepository():
    def __init__(self, session : AsyncSession):
        self.session = session
    async def create_chat(self, user_id : uuid.UUID, title: str ):
        try:
            title = title or "New Chat"
            chat = Chat(title=title)
            self.session.add(chat)
            await self.session.flush()
            await self.session.refresh(chat)
            user_chat = UserChat(user_id= user_id, chat_id= chat.id)
            self.session.add(user_chat)
            await self.session.commit()
            return chat
        except Exception:
            await self.session.rollback()

    async def get_user_chat(user_id : uuid.UUID, limit : int, offset: int):
        pass 
    async def get_chat_by_id(chat_id : uuid.UUID):
        pass
    async def update_chat_title(chat_id : uuid.UUID, chat_title : str):
        pass 
    async def delete_caht(chat_id : uuid.UUID):
        pass
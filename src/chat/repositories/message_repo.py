from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import uuid
from src.db.chat import Message, ChatRole
from src.db.user import User
class MessageRepository():
    def __init__(self, session :AsyncSession):
        self.session = session
    async def get_history(self, chat_id : uuid.UUID, window_size : int = 10 ):
        query = select(Message).where(
            Message.chat_id == chat_id
        ).order_by(Message.created_at.desc()).limit(window_size)
        result = await self.session.execute(query)
        messages = result.scalars().all()
        return messages[::-1]
    async def send_message(self, chat_id: uuid.UUID, user_id : uuid.UUID, role : ChatRole,  content :str, tokens : int):
        message = Message(chat_id=chat_id, user_id= user_id, role = role, content=content, tokens_count = tokens)
        try:
            self.session.add(message)
            await self.session.commit()
            await self.session.refresh(message)
            return message
        except Exception as e:
            await self.session.rollback()
        raise  e 
    async def add_message_pair(chat_id : uuid.UUID, user_messages : dict, assistant_message : dict):
        pass
    async def get_tokens_stat(user_id: uuid.UUID):
        pass
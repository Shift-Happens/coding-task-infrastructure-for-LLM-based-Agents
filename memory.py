from langchain.memory import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from redis import Redis
from typing import Dict, Any

class EnhancedMemory:
    def __init__(self, session_id: str, redis_url: str):
        self.history = RedisChatMessageHistory(
            session_id=session_id,
            url=redis_url
        )
        self.memory = ConversationBufferMemory(
            chat_memory=self.history,
            return_messages=True
        )
    
    def add_message(self, role: str, content: str) -> None:
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        else:
            self.memory.chat_memory.add_ai_message(content)

    def get_context(self) -> Dict[str, Any]:
        return self.memory.load_memory_variables({})
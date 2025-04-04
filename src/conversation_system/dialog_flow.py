from datetime import datetime
from typing import List, Dict
from src.core.utilities.log import logger
from openai.types.beta.threads import MessageContent
from src.data_management.db_manage import get_user_info


# 先想下如果是新的对话，如何新建并处理对应的数据库和属性数据库

class DialogDispatcher:
    def __init__(self):
        pass


    def dispatch(self, enter_message):
        pass

class DispatchMessage:
    def __init__(self, data: Dict):
        self.sender_id: str = data.get("sender_id")
        self.sender_type: str = data.get("sender_type", "user")
        self.receiver_id: str = data.get("receiver_id")
        self.room_id: str = data.get("room_id")
        self.task_type: str = data.get("task_type", "chat")
        self.is_group: bool = data.get("is_group", False)
        self.timestamp: int = data.get("timestamp", int(datetime.utcnow().timestamp()))

        self.message: List[MessageContent] = [
            MessageContent(m["type"], m["content"]) for m in data.get("message", [])
        ]

    def is_to_ai(self) -> bool:
        is_ai = get_user_info(self.receiver_id)[3]
        if is_ai:
            return True
        else:
            return False

    def to_dict(self) -> Dict:
        return {
            "sender_id": self.sender_id,
            "sender_type": self.sender_type,
            "receiver_id": self.receiver_id,
            "room_id": self.room_id,
            "task_type": self.task_type,
            "message": [{"type": m.type, "content": m.content} for m in self.message],
            "is_group": self.is_group,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"<IncomingMessage from {self.sender_id} to {self.receiver_id} at {self.timestamp}>"
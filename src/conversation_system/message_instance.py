from enum import Enum
from datetime import datetime
from typing import List, Dict
from openai.types.beta.threads import MessageContent
from src.data_management.db_manage import get_user_info

class DispatchMessage:
    def __init__(self, data: Dict):
        self.sender_id: str = data.get("sender_id")
        self.sender_type: UserType = UserType(data.get("sender_type", 0))
        self.receiver_id: str = data.get("receiver_id")
        self.room_id: str = data.get("room_id", "")
        self.task_type: str = data.get("task_type", "chat")
        self.is_group: bool = data.get("is_group", False)
        self.timestamp: int = data.get("timestamp", int(datetime.utcnow().timestamp()))

        m = data.get("message")
        if m["type"] == "text":
            self.message_type = MessageType.TEXT
            self.message = m["content"]
        elif m["type"] == "image":
            self.message_type = MessageType.IMAGE
            self.message = f"![image]({m['content']})"

        self.receiver_type: UserType = self.get_receiver_type()

    def get_receiver_type(self):
        is_ai = get_user_info(self.receiver_id)["is_ai"]
        return UserType.AI if is_ai else UserType.USER

    def to_dict(self) -> Dict:
        return {
            "sender_id": self.sender_id,
            "sender_type": self.sender_type.value,
            "receiver_id": self.receiver_id,
            "receiver_type": self.receiver_type.value,
            "room_id": self.room_id,
            "task_type": self.task_type,
            "message": self.message,
            "message_type": self.message_type.value,
            "is_group": self.is_group,
            "timestamp": self.timestamp,
        }

    def __repr__(self):
        return f"<IncomingMessage from {self.sender_id} to {self.receiver_id} at {self.timestamp}>"

class MessageType(Enum):
    TEXT = 0        # 文本
    IMAGE = 1       # 图片
    VIDEO = 2       # 视频
    AUDIO = 3       # 音频
    FILE = 4        # 文件
    LOCATION = 5    # 地理位置
    CONTACT = 6     # 联系人
    STICKER = 7     # 表情包
    EVENT = 8       # 事件
    OTHER = 9       # 其他

class UserType(Enum):
    USER = 0        # 普通用户
    AI = 1          # AI用户
    SYSTEM = 2      # 系统用户


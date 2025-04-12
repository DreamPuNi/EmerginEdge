import time
import threading
from src.core.utilities.log import logger
from src.data_management.db_manage import *
from src.conversation_system.message_instance import *
from src.prompt_engine.build_prompt import BuildPrompt
from src.core.middleware.queue_manage import get_dispatch_queue

# 先想下如果是新的对话，如何新建并处理对应的数据库和属性数据库

class DialogDispatcher:
    def __init__(self):
        self.dispatch_queue = get_dispatch_queue()

    def _parse_message_to_instance(self, raw_message: dict) -> DispatchMessage:
        """解析消息并返回 DispatchMessage 实例"""
        return DispatchMessage(raw_message)

    def _handler(self):
        """消息处理线程池，处理消息"""
        while not self.dispatch_queue.empty():
            message = self.dispatch_queue.get()
            self._process(message)
            self.dispatch_queue.task_done()

    def _process(self, message: DispatchMessage):
        """处理消息"""
        if message.is_group:
            room_id = message.room_id
            message_id = MessageIDGenerator().generate_id()
            insert_chat_message(
                message_id=message_id,
                user_id=message.sender_id,
                room_id=room_id,
                type=message.message_type.value,
                content=message.message
            )
        else:
            if message.room_id == "":
                room_id = "_".join(sorted([message.sender_id, message.receiver_id]))
                upsert_room(room_id, "private", 0)
            else:
                room_id = message.room_id
            message_id = MessageIDGenerator().generate_id()

            insert_chat_message(
                message_id=message_id,
                user_id=message.sender_id,
                room_id=room_id,
                type=message.message_type.value,
                content=message.message
            )

            if message.receiver_type == UserType.AI:
                # 这里需要把消息放到AI的队列里
                # 然后软件根据task_type来决定怎样处理消息
                # 决定好消息的处理方式，然后开始载入提示词，载入知识库和相关工具
                # 调用ai_services处理消息
                if message.task_type == "chat":
                    # TODO:调用build prompt
                    BuildPrompt
                pass
            elif message.receiver_type == UserType.USER:
                # 这里需要把消息放到用户的队列里
                # 然后软件根据task_type来决定怎样处理消息
                # 将处理完成后的消息放到用户的队列里
                # 然后调用用户的消息处理器
                pass

    def dispatch(self, enter_message: dict):
        """接受进入的消息并传递到队列"""
        parsed_message = self._parse_message_to_instance(enter_message)
        self.dispatch_queue.put(parsed_message)

class MessageIDGenerator:
    """消息ID生成器"""
    def __init__(self, machine_id: int = 1):
        self.machine_id = machine_id & 0x3FF
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _current_millis(self):
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp):
        timestamp = self._current_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_millis()
        return timestamp

    def generate_id(self):
        with self.lock:
            timestamp = self._current_millis()
            if self.last_timestamp == timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            self.last_timestamp = timestamp

            message_id = ((timestamp << 22) | (self.machine_id << 12) | self.sequence)

            return message_id
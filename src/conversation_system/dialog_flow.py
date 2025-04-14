import time
import threading
from src.core.utilities.log import logger
from src.data_management.db_manage import *
from src.conversation_system.message_instance import *
from src.prompt_engine.build_prompt import BuildPrompt
from src.core.middleware.queue_manage import get_dispatch_queue
from src.ai_services.routers.model_router import ai_services_router

class DialogDispatcher:
    def __init__(self):
        self.dispatch_queue = get_dispatch_queue()
        self.worker_thread = threading.Thread(target=self._handler, daemon=True)
        self.worker_thread.start()
        logger.info("DialogDispatcher initialized and worker thread started.")

    def _parse_message_to_instance(self, raw_message: dict) -> DispatchMessage:
        """解析消息并返回 DispatchMessage 实例"""
        logger.debug(f"Parsing raw message: {raw_message}")
        return DispatchMessage(raw_message)

    def _handler(self):
        """消息处理线程池，处理消息"""
        while True:
            message = self.dispatch_queue.get()
            logger.debug(f"Message received from queue: {message.sender_id} to {message.receiver_id}")
            try:
                self._process(message)
                logger.info(f"Processed message {message}")
            except Exception as e:
                logger.error(f"Error processing message {message}. Error: {e}")
            finally:
                self.dispatch_queue.task_done()

    def _process(self, message: DispatchMessage):
        """处理消息"""
        logger.debug(f"Processing message: {message}")

        # TODO: 群聊消息的完整处理
        if message.is_group:
            room_id = message.room_id
            message_id = MessageIDGenerator().generate_id()
            logger.info(f"Group message received. Inserting message into group {room_id} with message_id {message_id}.")
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
                logger.info(f"Private message. Created room {room_id} for sender {message.sender_id} and receiver {message.receiver_id}.")
            else:
                room_id = message.room_id
            message_id = MessageIDGenerator().generate_id()

            message.room_id = room_id
            message.task_id = message.task_type + "_" + str(message_id)

            logger.info(f"Inserting message into room {room_id} with task_id {message.task_id}.")
            insert_chat_message(
                message_id=message_id,
                user_id=message.sender_id,
                room_id=room_id,
                type=message.message_type.value,
                content=message.message
            )

            if message.receiver_type == UserType.AI:
                logger.info(f"Receiver is AI. Handling task type {message.task_type}.")
                if message.task_type == "chat":
                    ai_call_parameters = BuildPrompt(message).ai_services_input()
                    future = ai_services_router.route(ai_call_parameters)
                    reply = future.result()

                    def process_result(fut):
                        try:
                            reply = fut.result()
                            self._handle_ai_response(message,reply)
                        except Exception as e:
                            logger.error(f"Error processing AI response: {e}")

                    future.add_done_callback(process_result)
            elif message.receiver_type == UserType.USER:
                logger.info(f"Receiver is USER. No AI response required.")
                pass

    def _handle_ai_response(self,message: DispatchMessage, reply: dict):
        """处理AI的回复"""
        if reply.get("success"):
            reply_message_id = MessageIDGenerator().generate_id()
            insert_chat_message(
                message_id=reply_message_id,
                user_id=message.receiver_id,
                room_id=message.room_id,
                type=reply["message"][0]["type"],
                content=reply["message"][0]["content"]
            )
            logger.info(f"Task [{message.task_id}] response: {reply['message'][0]['content']}")

            # 这里需不需要再将AI回复的消息弄成DispatchMessage实例呢？
            # 这里进行后续分析任务的准备
        else:
            logger.error(f"Handle task {message.task_id}`s AI response failed.")


    def dispatch(self, enter_message: dict):
        """接受进入的消息并传递到队列"""
        logger.info(
            f"Dispatching incoming message: {enter_message.get('sender_id')} to {enter_message.get('receiver_id')}")
        parsed_message = self._parse_message_to_instance(enter_message)
        logger.info(f"Dispatching message: {parsed_message.sender_id} to {parsed_message.receiver_id}")
        self.dispatch_queue.put(parsed_message)
        logger.info(f"Message dispatched to queue for processing.")
        self.worker_thread.join()

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

            logger.debug(f"Generated message ID: {message_id}")
            return message_id
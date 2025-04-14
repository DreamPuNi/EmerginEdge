import time
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from src.core.utilities.log import logger
from src.data_management.db_manage import *
from src.conversation_system.message_instance import DispatchMessage


currrent_chat_map = defaultdict(list)
last_message_time = {}

def add_message(room_id: str, sender_type, message_type, content):
    currrent_chat_map[room_id].append({
        "role": sender_type,
        "message_type": message_type,
        "content": content
    })
    last_message_time[room_id] = datetime.now()

def check_and_analyze_all():
    now = datetime.now()
    for room_id, messages in currrent_chat_map.items():
        last_time = last_message_time.get(room_id)
        if not last_time:
            continue

        time_diff = now - last_time
        if time_diff > timedelta(minutes=30) and len(currrent_chat_map[room_id]) > 30:
            try:
                logger.info(f"Room {room_id} will be analyse.")
                task_id = "analyse_" + room_id + "_" +str(int(time.time()))

                analyse_chat(room_id, task_id, messages)

                currrent_chat_map.pop(room_id)
                last_message_time.pop(room_id)

                logger.info(f"Room {room_id} has been analysed.")
            except Exception as e:
                logger.error(f"Error analysing room {room_id}: {e}")

def analyse_chat(room_id, task_id, messages):
    # 这里拿到所有的组装的消息体，然后结合memory发送给AI进行处理
    room_info = get

    analyse_prompt = f"""
你是 AI 助理，负责分析与用户的聊天记录，并更新对用户的记忆。
你需要首先带入ai角色视角写下你对user的“印象”,并将其赋值为 user_impression。
接着，分析user和ai的相互之间的关系，并将其赋值为 supplement_prompt。
最后，总结出下次对话可能会用到的环境或其他背景信息，并将其赋值为narration_prompt。

【聊天内容】
{messages}

【当前记忆】


请你判断：
1. 是否有新的信息需要加入用户记忆？（true/false）
2. 如果需要，请以结构化格式返回 memory 更新内容（例如：姓名、爱好、观点、性格）

输出格式：
{
  "should_update": true,
  "new_memory": {
    "user_impression": "小明",
    "supplement_prompt": "摄影",
    "narration_prompt": "安静内向"
  }
}
    """
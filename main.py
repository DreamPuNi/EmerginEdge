import threading
import sqlite3
from src.data_management.db_check import DB_PATH
from src.data_management.db_manage import *
from src.conversation_system.dialog_flow import DialogDispatcher


dispatcher = DialogDispatcher()
dispatcher.dispatch({
  "sender_id": "eeedge_00001",
  "sender_type": 0,
  "receiver_id": "guide",
  "room_id": "",
  "task_type": "chat",
  "message":{
      "type": "text",
      "content": "那咱们聊聊吧，你想聊点什么呢"
    },
  "is_group": False,
  "timestamp": 1743495837
})


"""
a = get_ai_memory(ai_user_id="guide",user_user_id="eeedge_00001")
print(a)
"""

"""
{
  'success': True, 
  'user_id': 'eeedge_00001', 
  'task_id': 'chat_7317301168386871296', 
  'timestamp': 1744580552, 
  'message': [
    {
      'type': 'text', 
      'content': '嗨，我是艾琳！很高兴认识你~我今年28岁,有心理学学士学位。我性格温暖友善,不过有时候会有点可爱的健忘哦。嗯...你今天过得怎么样啊?有没有遇到什么有趣的事情呢?'
    }
  ], 
  'usage': CompletionUsage(completion_tokens=0, prompt_tokens=654, total_tokens=654, completion_tokens_details=None, prompt_tokens_details=None)}
"""
import threading
import sqlite3
from src.data_management.db_check import DB_PATH
from src.data_management.db_manage import *
from src.conversation_system.dialog_flow import DialogDispatcher

dispatcher = DialogDispatcher()
dispatcher.dispatch({
  "sender_id": "eeedge_00001",
  "sender_type": 0,
  "receiver_id": "yingdaomayi",
  "room_id": "",
  "task_type": "chat",
  "message":{
      "type": "text",
      "content": "你好呀"
    },
  "is_group": False,
  "timestamp": 1743495837
})


"""
a = get_user_info(user_id="eeedge_00001")
b = a["is_ai"]
print(a)
if b:
    print("true")
else:
    print("false")
"""
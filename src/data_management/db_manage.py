import sqlite3
from datetime import datetime
from src.core.utilities.log import logger
from src.data_management.db_check import DB_PATH

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 更新方法

def upsert_user(user_id, username, password, avatar=None, gender=None, is_ai=0):
    try:
        cursor.execute("""
            INSERT INTO user (user_id, user_name, password, avatar, gender, is_ai, created_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
                user_name = excluded.user_name,
                password = excluded.password,
                avatar = excluded.avatar,
                gender = excluded.gender
                is_ai = excluded.is_ai,
        """, (user_id, username, password, avatar, gender,is_ai, datetime.now()))
        conn.commit()
        logger.info(f"User {user_id} has been added or updated.")
    except sqlite3.IntegrityError as e:
        logger.error(f"User operation failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"User operation failed:{e}")

def insert_chat_message(message_id, user_id, room_id, type, content):
    try:
        cursor.execute("""
            INSERT INTO chat_message (message_id, user_id, room_id, type, create_time, content)
            VALUES (?,?,?,?,?,?)
        """,(message_id, user_id, room_id, type, datetime.now(),content))
        conn.commit()
        logger.debug(f"Message {message_id} insert successful.")
    except Exception as e:
        logger.error(f"Message {message_id} insert failed:{e}")

def upsert_room(room_id, name, room_type):
    try:
        cursor.execute("""
            INSERT INTO room (room_id, name, room_type, created_at)
            VALUES (?,?,?,?)
            ON CONFLICT(room_id) DO UPDATE SET
                name = excluded.name,
                room_type = excluded.room_type
        """, (room_id, name, room_type, datetime.now()))
        logger.debug(f"Room {room_id} has been added or updated.")
        conn.commit()
    except sqlite3.IntegrityError as e:
        logger.error(f"Room operation failed due to integrity issue:{e}.")
    except Exception as e:
        logger.error(f"Room {room_id} operation failed:{e}")

def add_user_to_room(room_id, user_id):
    try:
        cursor.execute("""
                INSERT INTO room_member (room_id, user_id, joined_at)
                VALUES (?,?,?)
            """, (room_id, user_id, datetime.now()))
        conn.commit()
        logger.debug(f"User {user_id} add to {room_id} successful.")
    except Exception as e:
        logger.error(f"User {user_id} add to {room_id} failed:{e}")

def upsert_ai_profile(ai_user_id, adapter, model_name, config_json, system_prompt):
    try:
        cursor.execute("""
            INSERT INTO ai_profile (ai_user_id, adapter, model_name, config_json, system_prompt)
            VALUES (?,?,?,?,?)
            ON CONFLICT(ai_user_id) DO UPDATE SET
                adapter = excluded.adapter,
                model_name = excluded.model_name,
                config_json = excluded.config_json,
                system_prompt = excluded.system_prompt
        """, (ai_user_id, adapter, model_name, config_json, system_prompt))
        conn.commit()
        logger.debug(f"AI profile for {ai_user_id} has been added or updated.")
    except sqlite3.IntegrityError as e:
        logger.error(f"AI profile operation failed due to integrity issue:{e}.")
    except Exception as e:
        logger.error(f"AI profile operation failed:{e}")

def upsert_ai_memory(ai_user_id, user_user_id, user_impression, supplement_prompt, narration_prompt):
    try:
        cursor.execute("""
            INSERT INTO ai_memory (ai_user_id, user_user_id, user_impression, supplement_prompt, narration_prompt)
            VALUES (?,?,?,?,?)
            ON CONFLICT(ai_user_id, user_user_id) DO UPDATE SET
                user_impression = excluded.user_impression,
                supplement_prompt = excluded.supplement_prompt,
                narration_prompt = excluded.narration_prompt
        """, (ai_user_id, user_user_id, user_impression, supplement_prompt, narration_prompt))
        conn.commit()
        logger.debug(f"AI memory for {ai_user_id} and {user_user_id} has been added or updated.")
    except sqlite3.IntegrityError as e:
        logger.error(f"AI memory operation failed due to integrity issue:{e}.")
    except Exception as e:
        logger.error(f"AI memory operation failed:{e}")

# 获取方法

def get_user_info(user_id):
    user_info = None
    try:
        cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            user_info = dict(row)
    except sqlite3.IntegrityError as e:
        logger.error(f"Get user info failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Get user info failed:{e}")
    return user_info

def get_roomlist_by_userid(user_id):
    room_list = []
    try:
        cursor.execute("SELECT * FROM room_member WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        room_list = [dict(row) for row in rows]
    except sqlite3.IntegrityError as e:
        logger.error(f"Get roomlist by userid failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Get roomlist by userid failed:{e}")
    return room_list

def get_room_info(room_id):
    room_info = None
    try:
        cursor.execute("SELECT * FROM room WHERE room_id = ?", (room_id,))
        row = cursor.fetchone()
        if row:
            room_info = dict(row)
    except sqlite3.IntegrityError as e:
        logger.error(f"Get roominfo failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Get roominfo failed:{e}")
    return room_info

def get_message_by_room(room_id):
    chat_history = None
    try:
        cursor.execute(
            """
            SELECT * FROM chat_message 
            WHERE room_id = ? 
            ORDER BY create_time ASC
            LIMIT 50
            """,
            (room_id,)
        )
        row = cursor.fetchall()
        if row:
            chat_history = [dict(r) for r in row]
    except sqlite3.IntegrityError as e:
        logger.error(f"Get chat history failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Get chat history failed:{e}")
    return chat_history

def get_ai_profile(ai_user_id):
    ai_profile = None
    try:
        cursor.execute("SELECT * FROM ai_profile WHERE ai_user_id = ?", (ai_user_id,))
        row = cursor.fetchone()
        if row:
            ai_profile = dict(row)
    except sqlite3.IntegrityError as e:
        logger.error(f"Get AI profile failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Get AI profile failed:{e}")
    return ai_profile

def get_ai_memory(ai_user_id, user_user_id):
    ai_memory = None
    try:
        cursor.execute("SELECT * FROM ai_memory WHERE ai_user_id = ? AND user_user_id = ?", (ai_user_id, user_user_id))
        row = cursor.fetchone()
        if row:
            ai_memory = dict(row)
    except sqlite3.IntegrityError as e:
        logger.error(f"Get AI memory failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Get AI memory failed:{e}")
    return ai_memory

# 删除方法

def delete_user(user_id):
    try:
        cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
        conn.commit()
        logger.info(f"User {user_id} has been deleted.")
    except sqlite3.IntegrityError as e:
        logger.error(f"Delete user {user_id} failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Delete user {user_id} failed:{e}")

def delete_room(room_id):
    try:
        cursor.execute("DELETE FROM room WHERE room_id = ?", (room_id,))
        cursor.execute("DELETE FROM room_member WHERE room_id = ?", (room_id,))
        # The chat_message table will not be deleted for now
        conn.commit()
        logger.info(f"Room {room_id} has been deleted.")
    except sqlite3.IntegrityError as e:
        logger.error(f"Delete room {room_id} failed, integrity error:{e}.")
    except Exception as e:
        logger.error(f"Delete room {room_id} failed:{e}")
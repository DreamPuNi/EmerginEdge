import os
import sqlite3
from src.core.utilities.log import logger

DB_DIR = "./database"
DB_NAME = "user_db.sqlite3"
DB_PATH = os.path.join(DB_DIR, DB_NAME)

EXPECTED_TABLES = {
    "user": """
        CREATE TABLE user (
            user_id TEXT UNIQUE PRIMARY KEY,
            user_name TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT,
            gender BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "chat_message": """
        CREATE TABLE chat_message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            user_id TEXT NOT NULL,
            room_id TEXT NOT NULL,
            type INTEGER NOT NULL,
            is_user BOOLEAN NOT NULL,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            content TEXT,
            FOREIGN KEY(user_id) REFERENCES user(user_id),
            FOREIGN KEY(room_id) REFERENCES room(room_id)
        );
    """,
    "room": """
        CREATE TABLE room (
            room_id TEXT PRIMARY KEY,
            name TEXT,
            room_type INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """,
    "room_member": """
        CREATE TABLE room_member (
            room_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (room_id, user_id),
            FOREIGN KEY (room_id) REFERENCES room(room_id),
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        );
    """
}

def check_database():
    if not os.path.exists(DB_DIR):
        os.mkdir(DB_DIR)

    if not os.path.exists(DB_PATH):
        logger.info(f"File {DB_PATH} not exist, being created.")
        create_database()
    else:
        logger.debug(f"Database detected, checking table structure.")
        if not check_tables():
            logger.info("Table structure does not match, recreate the database.")
            create_database()
        else:
            logger.debug("Correct structure.")

def check_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}

    if not EXPECTED_TABLES.keys() <= existing_tables:
        logger.info("Missing table:", EXPECTED_TABLES.keys() - existing_tables)
        return False

    for table, create_sql in EXPECTED_TABLES.items():
        cursor.execute(f"PRAGMA table_info({table});")
        columns = {row[1] for row in cursor.fetchall()}
        expected_columns = {
            line.split()[0]
            for line in create_sql.split("\n")
            if line.strip() and line.split()[0].islower()
        }

        if not expected_columns <= columns:
            logger.info(f"Table {table} missing columns:", expected_columns-columns)
            return False

    conn.close()
    return True

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for table, create_sql in EXPECTED_TABLES.items():
        cursor.execute(create_sql)

    conn.commit()
    conn.close()
    logger.info(f"Database {DB_NAME} created successful.")

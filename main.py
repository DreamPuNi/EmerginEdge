
import sqlite3
from src.data_management.db_check import DB_PATH
from src.data_management.db_manage import *

a = get_user_info(user_id="eeedge_00001")
print(a)
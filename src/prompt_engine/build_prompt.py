from src.conversation_system.message_instance import *
from src.data_management.db_manage import get_user_info
from src.prompt_engine.custom_prompt import system_prompt


class BuildPrompt:
    def __init__(self, message: DispatchMessage):
        self.sender_id = message.sender_id
        self.target_id = message.receiver_id
        self.target_type = message.receiver_type
        self.task_type = message.task_type

        role_args = get_user_info(self.target_id)

        self.r_system_prompt = role_args["system_prompt"]
        self.adapter = role_args["adapter"]
        self.model_name = role_args["model_name"]
        self.other_config = role_args["config_json"]

    def build_system_prompt(self):
        """构建系统提示词"""
        """
        目前 system prompt 主要是对这个角色向内的描述，与其他人无关，只包含和角色本体相关的内容
        然后和她对话的人的相关内容会在后面进行补充
        环境部分和动画控件的内容也会在后面进行补充
        """
        role_system_prompt = get_user_info(self.target_id)["system_prompt"]

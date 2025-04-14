import json
from src.core.utilities.log import logger
from src.conversation_system.message_instance import *
from src.data_management.db_manage import get_ai_profile, get_ai_memory, get_message_by_room

class BuildPrompt:
    def __init__(self, message: DispatchMessage):
        self.sender_id = message.sender_id
        self.target_id = message.receiver_id
        self.target_type = message.receiver_type
        self.task_type = message.task_type
        self.task_id = message.task_id
        self.room_id = message.room_id

        ai_profile = get_ai_profile(self.target_id)
        if ai_profile is None:
            logger.error(f"AI profile not found for {self.target_id}.")
        self.r_system_prompt = ai_profile.get("system_prompt", "")
        self.adapter = ai_profile.get("adapter", "openai")
        self.model_name = ai_profile.get("model_name", "gpt-3.5-turbo")
        self.other_config = ai_profile.get("config_json", """
            {
                "temperature": 0.5,
                "max_tokens": 100,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
        """
        )

        self._check_ai_memory()

    def _check_ai_memory(self):
        ai_memory = get_ai_memory(self.target_id, self.sender_id)
        try:
            self.user_impression = ai_memory.get("user_impression", "")
            self.supplement_prompt = ai_memory.get("supplement_prompt", "")
            self.narration_prompt = ai_memory.get("narration_prompt", "")
        except:
            logger.error(f"AI memory not found for {self.target_id} and {self.sender_id}.")
            self.user_impression = ""
            self.supplement_prompt = ""
            self.narration_prompt = ""

    def _build_system_prompt(self):
        """构建系统提示词"""
        """
        目前 system prompt 主要是对这个角色向内的描述，与其他人无关，只包含和角色本体相关的内容
        然后和她对话的人的相关内容会在后面进行补充
        环境部分和动画控件的内容也会在后面进行补充
        """
        system_prompt = self.r_system_prompt + self.supplement_prompt
        return system_prompt

    def _build_narration_prompt(self):
        """构建叙述提示词"""
        """
        叙述提示词主要是对这个角色当前对话背景的交代，包含和其他人相关的内容
        以及她对话的人的相关内容，以narration的角色出现在历史消息中
        """
        if self.narration_prompt != "":
            narration_prompt = {
                "role": "narration",
                "content": self.narration_prompt
            }
            return narration_prompt
        else:
            return None

    def _build_history(self):
        """构建历史消息"""
        history = []
        history.append(self._build_narration_prompt())
        history_list = get_message_by_room(self.room_id)
        for message in history_list:
            if message["user_id"] == self.sender_id:
                role = "user"
            else:
                role = "assistant"
            history.append({
                "role": role,
                "content": message["content"]
            })

        # TODO: 这里需要检查prompt长度限制

        return history

    def ai_services_input(self):
        """构建调用ai_services的管道消息体"""
        try:
            parameters = json.loads(self.other_config)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse other_config JSON: {e}")
            parameters = {}
        pull_up = {
            "user_id": self.sender_id,
            "task_id": self.task_id,
            "adapter": self.adapter,
            "model_name": self.model_name,
            "system_prompt": self._build_system_prompt(),
            "message": self._build_history(),
            "parameters": parameters,
        }
        logger.debug(f"AI services input: {pull_up}")
        return pull_up

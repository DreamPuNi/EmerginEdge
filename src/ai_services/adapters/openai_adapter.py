import openai
from retrying import retry
from config.config import conf
from src.core.utilities.log import logger
from src.ai_services.routers.model_to_url import model_to_url

class OpenAIAdapter(openai):
    def __init__(self, request_data):
        super().__init__()

        self.api_key = conf().get("openai_api_key")
        self.model_name = request_data.get("model_name")
        self.base_url = model_to_url.get(self.model_name)

        self.message = []
        if request_data.get("system_prompt"):
            self.message.append({
                "role": "system",
                "content": request_data.get("system_prompt")
            })
        self.message.extend(request_data.get("messages", []))

        parameters = request_data.get("parameters", {})
        for arg, value in parameters.items():
            setattr(self, arg, value)

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def handle(self):
        try:
            response = openai.ChatCompletion.create(
                model = self.model_name,
                messages = self.message,
                temperature = self.temperature if hasattr(self, "temperature") else 0.5,
                max_tokens = self.max_tokens if hasattr(self, "max_tokens") else 100,
                tpo_p = self.top_p if hasattr(self, "top_p") else 1,
                frequency_penalty = self.frequency_penalty if hasattr(self, "frequency_penalty") else 0,
                presence_penalty = self.presence_penalty if hasattr(self, "presence_penalty") else 0
            )
            return response
        except openai.OpenAIError as e:
            logger.error(f"OpenAI error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            raise

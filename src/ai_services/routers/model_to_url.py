from config.config import conf

model_to_url = {
    "openai": conf().get("openai_base_url"),
    "gpt-3.5-turbo": conf().get("openai_base_url")
}
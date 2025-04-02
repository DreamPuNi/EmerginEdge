from config.config import conf, load_config

load_config()
chatanywhere_url = conf().get("chatanywhere_url")

model_to_url = {
    "openai": chatanywhere_url,
    "gpt-3.5-turbo": chatanywhere_url,
    "gpt-4-0613": chatanywhere_url,
    "claude-3-7-sonnet-20250219": chatanywhere_url,
    "deepseek-r1": chatanywhere_url,
    "deepseek-v3": chatanywhere_url
}
import os
import json
from src.core.utilities.log import logger

available_settings = {
    # 模型设置
    # openai库参数设置
    'openai_api_key':"",
    'openai_base_url':"",
    'openai_model':"",
    'openai_temperature':0.5,
    'openai_max_tokens':100,
    'openai_top_p':1,
    'openai_frequency_penalty':0,
    'openai_presence_penalty':0,
}

class Config(dict):
    def __init__(self, config_dict=None):
        super().__init__()
        if config_dict is None:
            config_dict = {}
        for key, value in config_dict.items():
            self[key] = value

    def __getitem__(self, key):
        if key not in available_settings:
            raise KeyError(f"Invalid setting key: {key}")
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key not in available_settings:
            raise KeyError(f"Invalid setting key: {key}")
        return super().__setitem__(key, value)

    def get(self, key, default=None):
        return super().get(key, default)

    def set(self, key, value):
        self[key] = value

config = Config()

def load_config():
    global config
    config_path = "config/config.json"
    if not os.path.exists(config_path):
        logger.info("Config file not found, using config-template.json")
        config_path = "config/config-template.json"

    config_str = read_file(config_path)
    config = Config(json.loads(config_str))

def save_config():
    global config
    config_path = "config/config.json"
    try:
        config_dict = dict(config)
        sorted_config = {key: config_dict[key] for key in sorted(config_dict.keys())}
        with open(file=config_path, mode="w", encoding="utf-8") as f:
            f.write(json.dumps(sorted_config, indent=4, ensure_ascii=False))
            logger.info("Config saved to %s", config_path)
    except Exception as e:
        logger.error("Error saving config: %s", e)

def read_file(file_path):
    try:
        with open(file=file_path, mode="r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        logger.error("Error reading file: %s", e)
        raise

def conf():
    return config


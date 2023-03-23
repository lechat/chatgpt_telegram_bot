import yaml
import dotenv
from pathlib import Path


class Config(object):
    _instance = None

    @classmethod
    def get_instance(cls):

        if cls._instance is None:
            cls._instance = Config()

        return cls._instance

    def __init__(self):
        # get config directory
        config_dir = Path(__file__).parent.parent.resolve() / "config"
        # load yaml config
        with open(config_dir / "config.yml", "r") as f:
            config_yaml = yaml.safe_load(f)

        # load .env config
        config_env = dotenv.dotenv_values(config_dir / "config.env")

        # config parameters
        self.telegram_token = config_yaml["telegram_token"]
        self.openai_api_key = config_yaml["openai_api_key"]
        self.use_chatgpt_api = config_yaml.get("use_chatgpt_api", True)
        self.allowed_telegram_usernames = config_yaml["allowed_telegram_usernames"]
        self.new_dialog_timeout = config_yaml["new_dialog_timeout"]
        self.enable_message_streaming = config_yaml.get("enable_message_streaming", True)
        self.mongodb_uri = (
            f"mongodb://mongo:{config_env['MONGODB_PORT']}"
            if "MONGODB_PORT" in config_env
            else ""
        )
        self.redis_host = config_env.get("REDIS_HOST", "")
        self.redis_port = config_env.get("REDIS_PORT", "6379")

        # chat_modes
        with open(config_dir / "chat_modes.yml", "r") as f:
            self.chat_modes = yaml.safe_load(f)

        # prices
        self.chatgpt_price_per_1000_tokens = config_yaml.get(
            "chatgpt_price_per_1000_tokens", 0.002
        )
        self.gpt_price_per_1000_tokens = config_yaml.get("gpt_price_per_1000_tokens", 0.02)
        self.whisper_price_per_1_min = config_yaml.get("whisper_price_per_1_min", 0.006)

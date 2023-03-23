from abc import ABC, abstractmethod
from typing import Optional, Any

class Database(ABC):
    @abstractmethod
    def check_if_user_exists(
        self, user_id: int, raise_exception: bool = False
    ):
        pass

    @abstractmethod
    def add_new_user(
        self,
        user_id: int,
        chat_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
    ) -> None:
        pass

    @abstractmethod
    def start_new_dialog(self, user_id: int) -> None:
        pass

    @abstractmethod
    def get_user_attribute(self, user_id: int, key: str) -> Any:
        pass

    @abstractmethod
    def set_user_attribute(self, user_id: int, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def get_dialog_messages(
        self, user_id: int, dialog_id: Optional[str] = None
    ) -> list[dict]:
        pass

    @abstractmethod
    def set_dialog_messages(
        self,
        user_id: int,
        dialog_messages: list,
        dialog_id: Optional[str] = None,
    ) -> None:
        pass

    @staticmethod
    def load_db(config):
        if config.mongodb_uri != "":
            from bot.database_mongo import MongoDatabase

            return MongoDatabase(config.mongodb_uri)
        if config.redis_host != "":
            from bot.database_redis import RedisDatabase

            return RedisDatabase(config.redis_host, config.redis_port)

        raise Exception("No value for mongodb_uri or redis_host in config.yml")


from typing import Optional, Any, Mapping
import json

import redis
import uuid
from datetime import datetime
from contextlib import contextmanager

from bot.database import Database


class RedisDatabase(Database):
    """
    Redis database implementation.
    """
    def __init__(self, redis_host: str, redis_port: int):
        self.pool = redis.ConnectionPool(
            host=redis_host, port=redis_port, db=0
        )

    def _dt2str(self, dt: datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    def _bin2dt(self, bin: str):
        return datetime.strptime(bin, '%Y-%m-%d %H:%M:%S.%f')

    def _jsonstr(self, value: dict) -> str:
        return json.dumps(value)

    def _jsondict(self, value: bytes) -> dict[str, str] | list[dict]:
        return json.loads(value)

    @contextmanager
    def _connection(self):
        yield redis.Redis(connection_pool=self.pool)

    def check_if_user_exists(
        self, user_id: int, raise_exception: bool = False
    ):
        """
        Check if a user exists in the database.
        If the user does not exist, a ValueError will be raised.
        """
        user_key = f"user:{user_id}"
        with self._connection() as conn:
            if conn.exists(user_key):
                return True

        if raise_exception:
            raise ValueError(f"User {user_id} does not exist")
        else:
            return False

    def add_new_user(
        self,
        user_id: int,
        chat_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
    ):
        """
        Add a new user to the database.
        If the user already exists, a ValueError will be raised.
        """
        now_bytes = self._dt2str(datetime.now())
        user_dict = {
            "_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name if last_name else "",
            "last_interaction": now_bytes,
            "first_seen": now_bytes,
            "current_dialog_id": "",
            "current_chat_mode": "assistant",
            "n_used_tokens": 0,
        }

        if not self.check_if_user_exists(user_id):
            user_key = f"user:{user_id}"
            with self._connection() as conn:
                conn.set(user_key, self._jsonstr(user_dict))

    def _update_user(self, user_id, key, value):
        with self._connection() as conn:
            user = self._jsondict(conn.get(f"user:{user_id}"))
            user[key] = value
            conn.set(f"user:{user_id}", self._jsonstr(user))

    def start_new_dialog(self, user_id: int):
        """
        Start a new dialog for a user.
        If the user does not exist, a ValueError will be raised.
        """
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog_dict = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": self.get_user_attribute(user_id, "current_chat_mode"),
            "start_time": self._dt2str(datetime.now()),
            "messages": [],
        }

        with self._connection() as conn:
            # add new dialog
            conn.set(
                f"dialog:{dialog_id}:{user_id}",
                self._jsonstr(dialog_dict))

            self._update_user(user_id, "current_dialog_id", dialog_id)

        return dialog_id

    def get_user_attribute(self, user_id: int, key: str):
        """
        Get a user attribute.
        If the attribute does not exist, a ValueError will be raised.
        """
        self.check_if_user_exists(user_id, raise_exception=True)

        with self._connection() as conn:
            user = self._jsondict(conn.get(f"user:{user_id}"))
            if key not in user:
                raise ValueError(
                    f"User {user_id} does not have a value for {key}")
            else:
                if key == "last_interaction":
                    return self._bin2dt(user[key])
                if key == "n_used_tokens":
                    return int(user[key])

                return user[key]

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        """
        Set a user attribute.
        If the attribute does not exist, it will be created.
        """
        self.check_if_user_exists(user_id, raise_exception=True)

        if isinstance(value, datetime):
            value = self._dt2str(value)

        self._update_user(user_id, key, value)

    def get_dialog_messages(
        self, user_id: int, dialog_id: Optional[str] = None
    ) -> list[dict]:
        """
        Get the messages of a dialog.
        If no dialog_id is provided, the current dialog of the user
        will be used.
        """
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        with self._connection() as conn:
            msgbytes = conn.get(f"dialog:{dialog_id}:{user_id}")
            if msgbytes is None:
                return []

            return self._jsondict(msgbytes)["messages"]

    def set_dialog_messages(
        self,
        user_id: int,
        dialog_messages: list,
        dialog_id: Optional[str] = None,
    ):
        """
        Set the messages of a dialog.
        If no dialog_id is provided, the current dialog of the user
        will be used.
        """
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        encoded = []
        for msg in dialog_messages:
            if isinstance(msg["date"], datetime):
                msg["date"] = self._dt2str(msg["date"])
            encoded.append(msg)

        messages_key = f"dialog:{dialog_id}:{user_id}"
        with self._connection() as conn:
            conn.set(messages_key, self._jsonstr(encoded))

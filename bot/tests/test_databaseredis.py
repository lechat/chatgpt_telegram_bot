import pytest
from unittest import mock
from contextlib import contextmanager

from ..database_redis import RedisDatabase


class TestDatabaseRedis:
    @pytest.fixture
    def redisdb(self):
        return RedisDatabase("localhost", 6379)

    @contextmanager
    def _connection(self):
        yield mock.Mock()

    def test_check_if_user_exists(self, redisdb):
        user_id = 123
        user_key = f"user:{user_id}"
        with mock.patch.object(RedisDatabase, "_connection", self._connection):
            with mock.patch.object(
                RedisDatabase, "check_if_user_exists", return_value=True
            ) as mock_check_if_user_exists:
                redisdb.check_if_user_exists(user_id)
                mock_check_if_user_exists.assert_called_with(user_id)
                redisdb.check_if_user_exists(user_id, raise_exception=True)
                mock_check_if_user_exists.assert_called_with(
                    user_id, raise_exception=True
                )

    def test_add_new_user(self, redisdb):
        user_id = 123
        chat_id = 456
        username = "testuser"
        first_name = "Test"
        last_name = "User"
        user_dict = {
            "_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        }
        with mock.patch.object(RedisDatabase, "_connection", self._connection):
            with mock.patch.object(
                RedisDatabase, "add_new_user", return_value=user_dict
            ) as mock_add_new_user:
                redisdb.add_new_user(
                    user_id, chat_id, username, first_name, last_name
                )
                mock_add_new_user.assert_called_with(
                    user_id, chat_id, username, first_name, last_name
                )

    def test_start_new_dialog(self, redisdb):
        user_id = 123
        with mock.patch.object(RedisDatabase, "_connection", self._connection):
            with mock.patch.object(
                RedisDatabase, "start_new_dialog", return_value=None
            ) as mock_start_new_dialog:
                redisdb.start_new_dialog(user_id)
                mock_start_new_dialog.assert_called_with(user_id)

    def test_get_user_attribute(self, redisdb):
        user_id = 123
        key = "test_key"
        value = "test_value"
        with mock.patch.object(RedisDatabase, "_connection", self._connection):
            with mock.patch.object(
                RedisDatabase, "get_user_attribute", return_value=value
            ) as mock_get_user_attribute:
                val = redisdb.get_user_attribute(user_id, key)
                mock_get_user_attribute.assert_called_with(user_id, key)
                assert val == value

    def test_get_dialog_messages(self, redisdb):
        user_id = 123
        dialog_id = "test_dialog_id"
        with mock.patch.object(RedisDatabase, "_connection", self._connection):
            with mock.patch.object(
                RedisDatabase, "get_dialog_messages", return_value=[]
            ) as mock_get_dialog_messages:
                messages = redisdb.get_dialog_messages(user_id, dialog_id)
                mock_get_dialog_messages.assert_called_with(user_id, dialog_id)
                assert messages == []

    def test_set_dialog_messages(self, redisdb):
        user_id = 123
        dialog_id = "test_dialog_id"
        messages = [{"test": "test"}]
        with mock.patch.object(RedisDatabase, "_connection", self._connection):
            with mock.patch.object(
                RedisDatabase, "set_dialog_messages", return_value=None
            ) as mock_set_dialog_messages:
                redisdb.set_dialog_messages(user_id, messages, dialog_id)
                mock_set_dialog_messages.assert_called_with(
                    user_id, messages, dialog_id
                )

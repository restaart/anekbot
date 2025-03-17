from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError
from sqlalchemy import text

from app.chat_settings import get_chat_settings, set_chat_settings
from app.models import ChatSettings
from app.routes import set_settings

TEST_CHAT_ID = 1234


@pytest.fixture(autouse=True)
async def chat_settings_test_env(database_container, db_session):
    yield
    await db_session.execute(
        text("TRUNCATE TABLE chat_settings RESTART IDENTITY CASCADE")
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_default_chat_settings():
    default_settings = await get_chat_settings(TEST_CHAT_ID)
    assert default_settings == ChatSettings()


@pytest.mark.asyncio
async def test_set_chat_settings():
    settings = ChatSettings(joke_min_likes=10)
    await set_chat_settings(TEST_CHAT_ID, settings)
    saved_settings = await get_chat_settings(TEST_CHAT_ID)
    assert saved_settings == settings


@pytest.mark.asyncio
async def test_set_chat_settings():
    settings = ChatSettings(joke_min_likes=10)
    await set_chat_settings(TEST_CHAT_ID, settings)
    saved_settings = await get_chat_settings(TEST_CHAT_ID)
    assert saved_settings == settings


class MockChatMessage(AsyncMock):

    @classmethod
    def build(cls, chat_id, text, user="user"):
        message = cls()
        message.chat.id = chat_id
        message.text = text
        message.from_user.username = user
        return message

    def replied_with(self):
        if self.reply.call_count:
            return self.reply.call_args.args[0]


@pytest.mark.asyncio
async def test_set_chat_via_message_settings():
    message = MockChatMessage.build(
        chat_id=TEST_CHAT_ID, text="/set @bot joke_min_likes=10"
    )

    await set_settings(message)

    assert message.replied_with() == "Готово"

    saved_settings = await get_chat_settings(TEST_CHAT_ID)
    assert saved_settings.joke_min_likes == 10


@pytest.mark.asyncio
async def test_ignored_for_missing_auth_via_message_settings():
    message = MockChatMessage.build(
        chat_id=TEST_CHAT_ID, text="/set @bot joke_min_likes=10", user="not-admin"
    )

    await set_settings(message)

    assert message.replied_with() == None

    saved_settings = await get_chat_settings(TEST_CHAT_ID)
    assert saved_settings.joke_min_likes == 0


@pytest.mark.asyncio
async def test_error_set_settings():
    message = MockChatMessage.build(
        chat_id=TEST_CHAT_ID, text="/set @bot some_field=10"
    )

    with pytest.raises(ValidationError):
        await set_settings(message)

    assert message.replied_with() == "Не получилось"

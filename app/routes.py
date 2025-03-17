import logging
from random import random

from aiogram import Router, F
from aiogram.enums import ChatType, ContentType
from aiogram.filters import Command
from aiogram.types import Message

from app.bot_state import is_mentioned, BOT_STATE
from app.chat_settings import set_chat_settings, get_chat_settings
from app.database import get_session
from app.jokes import JokeRepository
from app.models import ChatSettings
from app.utils import auth_ok, get_message_text

router = Router()


@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    await set_chat_settings(message.chat.id, ChatSettings(enabled=True))
    await message.reply("Привет! Я рассказываю анекдоты к месту и не очень")


@router.message(Command(commands=["set"]))
async def set_settings(message: Message):

    if not auth_ok(message):
        return

    if message.chat.type != ChatType.PRIVATE and not is_mentioned(message.text):
        return

    message_text = (
        message.text.replace("/set", "")
        .replace(f"@{BOT_STATE['me'].username}", "")
        .strip()
    )
    try:
        settings_items = [pair.split("=") for pair in message_text.split()]
        settings = ChatSettings(**dict(settings_items))
        await set_chat_settings(message.chat.id, settings)
        await message.reply("Готово")
    except Exception as e:
        await message.reply("Не получилось")
        raise e


@router.message(
    F.content_type.in_(
        {
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.VIDEO,
        }
    )
)
async def send_joke(message: Message):
    message_text = get_message_text(message)
    if not message_text:
        return

    mentioned = is_mentioned(message_text)
    message_text = message_text.replace(f"@{BOT_STATE['me'].username}", "").strip()

    try:
        settings = await get_chat_settings(message.chat.id)
        if settings.enabled and any(
            [
                message.chat.type == ChatType.PRIVATE,
                mentioned,
                (len(message_text or "") > 200 and random() < 0.2),
            ]
        ):
            async with get_session() as session:

                joke_repo = JokeRepository(session)
                joke = await joke_repo.get_joke(
                    message_text,
                    min_likes=settings.joke_min_likes,
                    max_length=settings.joke_max_length,
                )
                if joke:
                    await message.reply(joke.text)

    except Exception as e:
        await message.reply("Что то сломалось (это не шутка)")
        logging.getLogger().exception(e)

import asyncio
import logging
from random import random

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message, ContentType

from app.chat_settings import get_chat_settings, set_chat_settings
from app.config import get_settings
from app.database import get_session
from app.jokes import JokeRepository
from app.models import ChatSettings

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize router
router = Router()
settings = get_settings()
bot = Bot(token=settings.tg_token)

BOT_STATE = {}


def auth_ok(message: Message) -> bool:
    return message.from_user.username in settings.admin_usernames


def is_mentioned(message_text: str):
    return BOT_STATE["me"].username in message_text


@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    await set_chat_settings(message.chat.id, ChatSettings(enabled=True))
    await message.reply("Привет! Я рассказываю анекдоты к месту и не очень")


def get_message_text(message: Message):
    match message.content_type:
        case ContentType.TEXT:
            text = message.text
        case ContentType.VIDEO | ContentType.PHOTO:
            text = message.caption
        case _:
            return None

    return text



@router.message(Command(commands=["set"]))
async def set_settings(message: Message):

    if not auth_ok(message):
        return

    if message.chat.type != ChatType.PRIVATE and not is_mentioned(message.text):
        return

    message_text = message.text.replace("/set", "").replace(f"@{BOT_STATE['me'].username}", "").strip()
    try:
        settings_items = [
            pair.split("=") for pair in message_text.split()
        ]
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


async def main():
    dp = Dispatcher()
    dp.include_router(router)

    BOT_STATE["me"] = await bot.me()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

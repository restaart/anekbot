import asyncio
import logging
from random import random

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message, ContentType

from app.config import settings
from app.database import async_session
from app.jokes import JokeRepository

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize router
router = Router()
bot = Bot(token=settings.tg_token)

BOT_STATE = {}


def auth_ok(message: Message) -> bool:
    return message.from_user.username in settings.admin_usernames


def is_mentioned(message_text:str):
    return BOT_STATE["me"].username in message_text


@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    await message.reply("Привет! Я рассказываю анекдоты к месту и не очень")


def get_message_text(message:Message):
    match message.content_type:
        case ContentType.TEXT:
            return message.text
        case ContentType.VIDEO | ContentType.PHOTO:
            return message.caption
        case _:
            return None


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
    try:
        if any(
            [
                is_mentioned(message_text),
                message.chat.type == ChatType.PRIVATE,
                (len(message_text or "") > 200 and random() < 0.2),
            ]
        ):
            async with async_session() as session:

                joke_repo = JokeRepository(session)
                joke = await joke_repo.get_joke(message_text, min_likes=500)
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

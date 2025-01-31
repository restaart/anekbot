import asyncio
import logging
from random import random

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message, ContentType

from app.ai import get_photo_description
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize router
router = Router()
bot = Bot(token=settings.TG_TOKEN)


def auth_ok(message: Message) -> bool:
    return message.from_user.username in settings.ADMIN_USERNAMES


def is_mentioned(message: Message) -> bool:
    if not message.entities:
        return False

    for entity in message.entities:
        if entity.type == "mention":
            mention_text = message.text[entity.offset : entity.offset + entity.length]
            if mention_text == settings.BOT_NAME:
                return True
    return False


@router.message(Command(commands=["start", "help"]))
async def send_welcome(message: Message):
    await message.reply("Привет! Я рассказываю анекдоты к месту и не очень")


# @router.message(Command(commands=['health']))
# async def health(message: Message):
#     await message.reply(pformat(bot_storage.data))


async def process_joke(message: Message) -> str | None:
    logging.info(f"User: {message.from_user}")

    if (
        message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]
        and message.reply_to_message
        and is_mentioned(message)
    ):
        message = message.reply_to_message

    text = message.text or message.caption or ""
    text = "".join(text.split(settings.BOT_NAME)).strip()

    if not (text or message.photo):
        return None

    if message.photo:
        photo_url = await message.photo[-1].get_url()
        description = get_photo_description(photo_url)
        text += f" {description}"

    logging.info(f"Text: {text}")
    # return storage.get_random_joke(text.strip(), top=3)


@router.message(lambda message: message.photo)
async def handle_photo(message: Message):
    # Get the largest photo (best quality)
    photo = message.photo[-1]

    # Get file_id
    file_id = photo.file_id

    # Get file info
    file = await bot.get_file(file_id)

    # Get file path
    file_path = file.file_path

    # Construct full URL
    # Note: Replace 'YOUR_BOT_TOKEN' with your actual bot token
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"

    await message.reply(f"Photo URL: {file_url}")


@router.message(F.content_type.in_({ContentType.TEXT, ContentType.PHOTO}))
async def send_joke(message: Message):
    print(message)
    await message.reply(message.photo)
    return
    try:
        if any(
            [
                is_mentioned(message),
                message.chat.type == ChatType.PRIVATE,
                (message.photo and random() < 0.2),
                (len(message.text or "") > 200 and random() < 0.2),
            ]
        ):
            joke = await process_joke(message)
            if joke:
                await message.reply(joke)
                bot_storage.increment_served(message.from_user.username)

    except Exception as e:
        await message.reply("Что то сломалось (это не шутка)")
        logging.getLogger().exception(e)
        bot_storage.increment_errors()


async def main():

    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot_state import init_bot_state
from app.config import settings
from app.routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize router

bot = Bot(token=settings.tg_token)


async def main():
    dp = Dispatcher()
    dp.include_router(router)

    await init_bot_state(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

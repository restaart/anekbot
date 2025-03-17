from aiogram import Bot

BOT_STATE = {}


def is_mentioned(message_text: str):
    return BOT_STATE["me"].username in message_text


async def init_bot_state(bot: Bot):
    me = await bot.get_me()
    BOT_STATE["me"] = me

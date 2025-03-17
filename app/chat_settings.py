from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import ChatSettings, ChatSettingsDB


async def get_chat_settings(
    chat_id: int | str, session: AsyncSession = None
) -> ChatSettings:

    chat_id = str(chat_id)
    async with session or get_session() as session:
        result = await session.execute(
            select(ChatSettingsDB).where(ChatSettingsDB.chat_id == chat_id)
        )
        chat_settings = result.scalars().first()
        if chat_settings is None or chat_settings.settings is None:
            return ChatSettings()
        return ChatSettings(**chat_settings.settings)


async def set_chat_settings(
    chat_id: int | str, settings: ChatSettings, session: AsyncSession = None
) -> None:

    chat_id = str(chat_id)
    settings_dict = settings.model_dump(exclude_defaults=True)
    async with session or get_session() as session:
        result = await session.execute(
            select(ChatSettingsDB).where(ChatSettingsDB.chat_id == chat_id)
        )
        chat_settings = result.scalars().first()
        if chat_settings is None:
            chat_settings = ChatSettingsDB(chat_id=chat_id, settings=settings_dict)
        else:
            chat_settings.settings = settings_dict

        await session.merge(chat_settings)

        await session.commit()


if __name__ == "__main__":

    async def main():
        chat_id = "1213"
        async with get_session() as session:
            settings = await get_chat_settings(chat_id, session)
            print(settings)
            settings.joke_min_likes = 0
            await set_chat_settings(chat_id, settings, session)

    import asyncio

    asyncio.run(main())

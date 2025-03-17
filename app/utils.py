from aiogram.enums import ContentType
from aiogram.types import Message

from app.config import settings


def auth_ok(message: Message) -> bool:
    return message.from_user.username in settings.admin_usernames


def get_message_text(message: Message):
    match message.content_type:
        case ContentType.TEXT:
            text = message.text
        case ContentType.VIDEO | ContentType.PHOTO:
            text = message.caption
        case _:
            return None

    return text

from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from src.db import User, Room
from src.utils import inline_builder

router = Router()


@router.message(
    F.content_type.in_(
        [
            "text", "audio", "voice",
            "sticker", "document", "photo",
            "video"
        ]
    ),
    flags={"no_throttle": True}
)
async def send_message(message: Message, user: User):
    if not user or not user.current_room:
        return

    room = await Room.get(user.current_room)
    await room.send_copy(message, not_to_user_id=user.user_id)

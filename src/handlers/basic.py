import math

from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from src.db import User, Room
from src.utils import inline_builder

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message, command: CommandObject, user: User):
    if not user:
        user = User(
            user_id=message.from_user.id
        )

        await user.insert()
        logger.debug(f"registered new user with id {message.from_user.id}")

    if not command.args or len(command.args) != 5:
        text = (
            f"<b>Hello, {message.from_user.full_name}</b>\n"
            "<i>I'm anonymous chat bot. You can create new room below</i>"
        )

        await message.reply(text, reply_markup=inline_builder(["Create room", "new_room"]))
        return

    if user.current_room:
        pattern = dict(
            text="<b><i>You already in a room. Do you want to leave it?</i></b>",
            reply_markup=inline_builder(["Leave", "leave"])
        )
        await message.answer(**pattern)
        return

    room = await Room.find_one(Room.invitation == command.args, fetch_links=True)
    if len(room.users) + 1 > room.limit:
        await message.answer(f"<b>This room is full. {len(room.users)}/{room.limit}</b>")
        return

    room.users.append(user)

    user.current_room = room.id

    await room.send("Someone join this room...", message.bot)

    await user.save()
    await room.save()

    await message.answer("<b>You have successfully joined the room</b>")

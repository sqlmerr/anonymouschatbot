import random
from typing import Union
from random import choice

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.db import User, Room
from src.utils import inline_builder

router = Router()


@router.callback_query(F.data == "leave")
@router.message(Command("leave"))
async def leave_room(event: Union[Message, CallbackQuery], user: User):
    if isinstance(event, CallbackQuery):
        await event.answer()

    if not user.current_room:
        pattern = dict(
            text="<b><i>You are no longer in the room</i></b>"
        )

        if isinstance(event, Message):
            await event.answer(**pattern)
        else:
            await event.message.answer(**pattern)
        return

    room: Room = await Room.find_one(Room.id == user.current_room, fetch_links=True)
    room.users.remove(user)
    await room.send("Someone leave this room...", event.bot)
    await room.save()

    if len(room.users) > 0:
        if room.owner.user_id == user.user_id:
            await room.send("Сhoosing a new owner for this room...", event.bot)
            owner = choice(room.users)
            room.owner = owner
            await event.bot.send_message(owner.user_id, "You are new owner of this room!")
        await room.save()
    else:
        await room.delete()

    user.current_room = None
    await user.save()

    text = "<b>You have successfully leave the room!</b>"
    if isinstance(event, Message):
        await event.answer(text)
    else:
        await event.message.answer(text)

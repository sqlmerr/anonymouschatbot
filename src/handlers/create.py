import uuid

from typing import Union
from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.db import User, Room
from src.utils import inline_builder, CreateRoomState

router = Router()


@router.callback_query(F.data == "new_room")
@router.message(Command("create"))
async def create_room(event: Union[Message, CallbackQuery], state: FSMContext, user: User):
    if isinstance(event, CallbackQuery):
        await event.answer()

    if user.current_room:
        pattern = dict(
            text="<b><i>You already in a room. Do you want to leave it?</i></b>",
            reply_markup=inline_builder(["Leave", "leave"])
        )

        if isinstance(event, Message):
            await event.answer(**pattern)
        else:
            await event.message.answer(**pattern)
        return

    await state.set_state(CreateRoomState.name)

    if isinstance(event, Message):
        await event.answer("<b><i>How are we going to call it?</i></b>")
    else:
        await event.message.answer("<b><i>How are we going to call it?</i></b>")


@router.message(F.text, CreateRoomState.name)
async def create_room_name(message: Message, state: FSMContext, user: User):
    if user.current_room:
        pattern = dict(
            text="<b><i>You already in a room. Do you want to leave it?</i></b>",
            reply_markup=inline_builder(["Leave", "leave"])
        )
        await message.answer(**pattern)
        await state.clear()
        return

    name = message.text
    if len(name) > 32:
        await message.answer("<b>Name is too long!</b>")
        return

    room = Room(
        name=name,
        owner=user,
        users=[user],
        invitation=str(uuid.uuid4())[:5]
    )
    await room.insert()
    await state.clear()

    user.current_room = room.id
    await user.save()

    bot = await message.bot.get_me()
    link = f"t.me/{bot.username}/?start={room.invitation}"
    text = (
        f"<b>A new room named {name} has been successfully created!</b>\n"
        f"<i>join link: </i><code>{link}</code>"
    )

    await message.answer(text)

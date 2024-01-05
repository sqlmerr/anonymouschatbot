from contextlib import suppress

from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message


from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Next, Cancel, Back, SwitchTo, Counter, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.api.exceptions import UnknownIntent

from src.db import Room, User, get_room


class ManageDialog(StatesGroup):
    greeting = State()
    change_name = State()
    change_limit = State()
    delete = State()


async def getter(dialog_manager: DialogManager, **kwargs) -> dict:
    with suppress(TypeError):
        room: Room = await get_room(dialog_manager.start_data["room_id"])

        return {
            "visibility": "🌏 public" if room.visibility else "❌  private",
            "name": room.name,
            "users": len(room.users),
            "limit": room.limit,
        }


async def change_visibility(c: CallbackQuery, _: Button, manager: DialogManager, **kwargs):
    with suppress(TypeError):
        room: Room = await get_room(manager.start_data["room_id"])
        if c.from_user.id != room.owner.user_id:
            return

        room.visibility = not room.visibility
        await room.save()
        await c.answer()


async def change_name(m: Message, _, manager: DialogManager, *args, **kwargs):
    with suppress(TypeError):
        room: Room = await get_room(manager.start_data["room_id"])
        if m.from_user.id != room.owner.user_id:
            return

        if len(m.text) > 32:
            await m.answer("<b>Too long</b>")
            return

        room.name = m.text
        await room.save()
        await m.answer(f"<b>Successfully changed name to {m.text}</b>")


async def change_limit(c: CallbackQuery, _, manager: DialogManager, **kwargs):
    with suppress(TypeError):
        room: Room = await get_room(manager.start_data["room_id"])
        if c.from_user.id != room.owner.user_id:
            return
        counter: Counter = manager.find("change_limit_counter")
        data = counter.get_widget_data(manager, counter.default)
        room.limit = int(data)
        await room.save()

        await c.answer("Success")
        await manager.switch_to(ManageDialog.greeting)


async def delete_room(c: CallbackQuery, _, manager: DialogManager, **kwargs):
    with suppress(TypeError):
        room: Room = await get_room(manager.start_data["room_id"])
        if c.from_user.id != room.owner.user_id:
            return

        await room.send("This room has been deleted by owner", c.bot, not_to_user_id=c.from_user.id)
        for user in room.users:
            user.current_room = None
            await user.save()
        await room.delete()

        await c.answer("Room successfully deleted!", True)
        await manager.done()


dialog = Dialog(
    Window(
        Format("<b>📎 Managing group {name}</b>\n<i>Total {users} users</i>\n<i>Limit: {limit}</i>"),
        Button(
            Format("{visibility}"),
            id="change_visibility",
            on_click=change_visibility,
        ),
        Next(
            Const("Change name"),
            id="change_name"
        ),
        SwitchTo(
            Const("Change limit"),
            id="change_limit",
            state=ManageDialog.change_limit
        ),
        SwitchTo(
            Const("⚠️ Delete"),
            id="delete",
            state=ManageDialog.delete
        ),
        Cancel(),
        state=ManageDialog.greeting,
        getter=getter
    ),
    Window(
        Const("<b>Please write new name of this room</b>"),
        TextInput(
            id="change_name",
            on_success=change_name
        ),
        Back(),
        state=ManageDialog.change_name
    ),
    Window(
        Const("<b>Choose new limit</b>"),
        Counter(
            id="change_limit_counter",
            min_value=1,
            max_value=100,
            default=10
        ),
        Button(
            Const("Save"),
            id="save_limit",
            on_click=change_limit
        ),
        SwitchTo(
            Const("Back"),
            id="__back__",
            state=ManageDialog.greeting
        ),
        state=ManageDialog.change_limit
    ),
    Window(
        Const("⚠️ <b>Are you sure you want to delete this room?</b>"),
        Row(
            Button(
                Const("yes"),
                id="delete_yes",
                on_click=delete_room
            ),
            SwitchTo(
                Const("no"),
                id="delete_no",
                state=ManageDialog.greeting,
            )
        ),
        state=ManageDialog.delete
    )
)




from loguru import logger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, ExceptionTypeFilter

from src.db import User, Room
from src.utils import inline_builder

from aiogram_dialog import DialogManager, StartMode, setup_dialogs, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from src.dialogs.manage import dialog, ManageDialog

router = Router()
router.include_router(dialog)
setup_dialogs(router)


@router.message(Command("manage"))
async def manage_cmd(message: Message, dialog_manager: DialogManager, user: User):
    if not user.current_room:
        await message.answer("<b><i>You are no longer in the room</i></b>")
        return

    room = await Room.get(user.current_room, fetch_links=True)
    if room.owner.user_id != user.user_id:
        await message.answer("<b><i>You aren't owner of this room!</i></b>")
        return

    await dialog_manager.start(ManageDialog.greeting, data={"user_id": user.user_id})


@router.errors(ExceptionTypeFilter(UnknownState))
@router.errors(ExceptionTypeFilter(UnknownIntent))
async def dialog_error(event, dialog_manager: DialogManager):
    logger.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        ManageDialog.greeting, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,
    )

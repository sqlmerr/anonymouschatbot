from aiogram import Bot, types

from typing import List, Optional
from beanie import Document, Indexed, Link, PydanticObjectId
from pydantic import Field


class User(Document):
    user_id: Indexed(int, unique=True)
    current_room: Optional[PydanticObjectId] = None


class Room(Document):
    name: str
    owner: Link[User]
    users: List[Link[User]]
    invitation: str
    limit: int = 10
    visibility: bool = True  # True - public, False - private

    async def send(self, message: str, bot: Bot, not_to_user_id: Optional[int] = None, **kwargs):
        for user in self.users:
            if not isinstance(user, User):
                user = await user.fetch()
            if not_to_user_id and user.user_id != not_to_user_id:
                await bot.send_message(user.user_id, message, **kwargs)
            elif not not_to_user_id:
                await bot.send_message(user.user_id, message, **kwargs)

    async def send_copy(self, message: types.Message, not_to_user_id: Optional[int] = None, **kwargs):
        for user in self.users:
            if not isinstance(user, User):
                user = await user.fetch()
            if not_to_user_id and user.user_id != not_to_user_id:
                await message.send_copy(user.user_id, **kwargs)
            elif not not_to_user_id:
                await message.send_copy(user.user_id, **kwargs)

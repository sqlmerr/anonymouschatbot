from beanie import PydanticObjectId
from .models import User, Room


async def get_user(user_id: int):
    return await User.find_one(User.user_id == user_id, fetch_links=True)


async def get_room(room_id: PydanticObjectId):
    return await Room.get(room_id, fetch_links=True)

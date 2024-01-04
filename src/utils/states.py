from aiogram.fsm.state import State, StatesGroup


class CreateRoomState(StatesGroup):
    name = State()

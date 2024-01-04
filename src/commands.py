from aiogram import Bot
from aiogram.types import BotCommandScopeDefault, BotCommand


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="start bot"),
        BotCommand(command="manage", description="manage current room, if you're owner"),
        BotCommand(command="leave", description="leave from current room"),
    ]

    return await bot.set_my_commands(
        commands,
        BotCommandScopeDefault()
    )

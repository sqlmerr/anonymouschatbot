from aiogram import Router
from . import basic, create, leave, sender


def register_routers() -> Router:
    router = Router()

    router.include_routers(
        basic.router,
        create.router,
        leave.router,
        sender.router,
    )

    return router

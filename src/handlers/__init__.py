from aiogram import Router
from . import basic, create, leave, sender, manage


def register_routers() -> Router:
    router = Router()

    router.include_routers(
        basic.router,
        create.router,
        leave.router,
        manage.router,
        sender.router,
    )

    return router

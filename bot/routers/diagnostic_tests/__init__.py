from aiogram import Router

from .view import router as view_router
from .actions import router as actions_router

router = Router()

router.include_router(view_router)
router.include_router(actions_router)

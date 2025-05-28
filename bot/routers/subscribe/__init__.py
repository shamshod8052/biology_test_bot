from aiogram import Router

from .view import router as view_router

router = Router()

router.include_router(view_router)

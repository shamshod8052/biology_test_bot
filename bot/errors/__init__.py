from aiogram import Router

from .error import router as error_router

router = Router()

router.include_router(error_router)

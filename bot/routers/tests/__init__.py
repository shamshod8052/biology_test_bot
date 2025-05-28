from aiogram import Router

from .view_tests_list import router as view_tests_list_router
from .view_test_info import router as view_test_info_router
from .begin_test import router as begin_test_router
from .receive_answers import router as receive_answers_router
from .next_test import router as next_test_router
from .stop_test import router as stop_test_router

router = Router()

router.include_router(view_tests_list_router)
router.include_router(view_test_info_router)
router.include_router(begin_test_router)
router.include_router(receive_answers_router)
router.include_router(next_test_router)
router.include_router(stop_test_router)

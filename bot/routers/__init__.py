from aiogram import Router

from .set_main_menu import router as set_main_menu_router
from .main_commands import router as main_commands_router
from .tests import router as tests_router
from .courses import router as courses_router
from .video_lessons import router as video_lessons_router
from .subscribe import router as subscribe_router
from .diagnostic_tests import router as diagnostic_tests_router

router = Router()

router.include_router(set_main_menu_router)
router.include_router(main_commands_router)
router.include_router(tests_router)
router.include_router(courses_router)
router.include_router(video_lessons_router)
router.include_router(subscribe_router)
router.include_router(diagnostic_tests_router)

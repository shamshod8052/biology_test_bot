from aiogram import F, Router
from aiogram.types import Message

from bot.filters.multilang_utils import get_translations

router = Router(name=__name__)


@router.message(F.text.in_(get_translations("Attestation courses")))
async def attestation_courses(message: Message):
    from Attestation.models import Course

    await message.answer(Course.objects.get_text())

@router.message(F.text.in_(get_translations("Certificate courses")))
async def certificate_courses(message: Message):
    from Certificate.models import Course

    await message.answer(Course.objects.get_text())

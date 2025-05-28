from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from django.core.paginator import Paginator as DjangoPaginator

from Attestation.models import DiagnosticTest as attestation_diagnostic
from Certificate.models import DiagnosticTest
from bot.filters.multilang_utils import get_translations
from bot.filters.states import Keyboard
from bot.functions.objects_to_text import get_objects_text
from bot.keyboards.diagnostic_tests import diag_tests

router = Router(name=__name__)


@router.message(F.text.in_(get_translations("Diagnostic tests")), Keyboard.attestation)
async def attestation_diagnostic_func(message: Message):
    text = attestation_diagnostic.objects.get_text()

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text.in_(get_translations("Diagnostic tests")), Keyboard.certificate)
async def certificate_diagnostic_func(message: Message):
    per_page = 2
    queryset = DiagnosticTest.objects.filter(is_active=True).all()
    text = get_objects_text(queryset, 'name', rows_num=per_page)
    keyboard = diag_tests(1, per_page=2)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


@router.callback_query(F.data.startswith('page_diag_test:'))
async def certificate_diagnostic_func(call: CallbackQuery):
    page_number = int(call.data.split(":")[1])
    per_page = 2
    queryset = DiagnosticTest.objects.filter(is_active=True).all()
    text = get_objects_text(queryset, 'name', per_page, page_number)
    keyboard = diag_tests(page_number, per_page)

    await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text.in_(get_translations("Diagnostic tests")))
async def diagnostic(message: Message):
    await message.answer("👉 /start /start 👈")

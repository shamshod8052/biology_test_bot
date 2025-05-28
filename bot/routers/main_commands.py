from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from django.utils.translation import gettext_lazy as _

from bot.filters.multilang_utils import get_translations
from bot.filters.states import Keyboard
from bot.keyboards import test_titles_kb
from bot.keyboards.main_menus import attestation_menu_kb
from bot.keyboards.main_menus import certificate_menu_kb

router = Router(name=__name__)

@router.message(F.text.in_(get_translations("Tests")))
async def get_titles(message: types.Message):
    await message.answer(
        str(_("Choose one of the tests and take the test!")), reply_markup=test_titles_kb()
    )

@router.callback_query(F.data.startswith("page_lr_title:"))
async def back2titles(call: types.CallbackQuery):
    page_num = int(call.data.split(":")[1])
    await call.message.edit_text(
        str(_("Choose one of the tests and take the test!")), reply_markup=test_titles_kb(page_num)
    )


@router.callback_query(F.data == 'back2titles')
async def back2titles(call: types.CallbackQuery):
    await call.message.edit_text(
        str(_("Choose one of the tests and take the test!")), reply_markup=test_titles_kb()
    )

@router.message(F.text.in_(get_translations("Attestation")))
async def test_stop(message: Message, state: FSMContext):
    await state.set_state(Keyboard.attestation)
    await message.answer(str(_("Choose one of the menus!")), reply_markup=attestation_menu_kb())

@router.message(F.text.in_(get_translations("Certificate")))
async def test_stop(message: Message, state: FSMContext):
    await state.set_state(Keyboard.certificate)
    await message.answer(str(_("Choose one of the menus!")), reply_markup=certificate_menu_kb())

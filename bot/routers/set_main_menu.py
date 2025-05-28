from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from django.utils.translation import gettext_lazy as _

from Admin.models import User
from bot.filters.multilang_utils import get_translations
from bot.keyboards.main_menus import main_menu_kb

router = Router(name=__name__)


@router.message(Command("start"))
async def on_start(message: types.Message, user: User, state: FSMContext):
    await state.clear()
    await message.answer(
        _("Salom, {first_name}").format(first_name=user.first_name),
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == 'main_menu')
async def main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer(str(_("Main menu")), reply_markup=main_menu_kb())


@router.message(F.text.in_(get_translations("Main menu")))
async def main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(str(_("Main menu")), reply_markup=main_menu_kb())

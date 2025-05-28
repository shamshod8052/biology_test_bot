from aiogram import Router, types, F
from django.utils.translation import gettext_lazy as _

from bot.keyboards.tests import title_tests_kb

router = Router(name=__name__)


@router.callback_query(F.data.startswith('title:'))
async def get_title_tests(call: types.CallbackQuery):
    title_pk = int(call.data.split(':')[1])

    await call.message.edit_text(
        str(_("Choose one of the tests for the title...")),
        reply_markup=title_tests_kb(title_pk)
    )


@router.callback_query(F.data.startswith('page_title:'))
async def get_title_tests(call: types.CallbackQuery):
    title_pk = int(call.data.split(':')[1])
    page_num = int(call.data.split(':')[2])

    await call.message.edit_text(
        str(_("Choose one of the tests for the title...")),
        reply_markup=title_tests_kb(title_pk, page_num)
    )

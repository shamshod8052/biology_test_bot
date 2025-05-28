from aiogram import Router, types, F

from bot.keyboards.tests import begin_kb
from Test.models import Test

router = Router(name=__name__)


@router.callback_query(F.data.startswith('test:'))
async def test_info(call: types.CallbackQuery):
    test_pk = int(call.data.split(':')[1])
    test = Test.objects.get(pk=test_pk)

    await call.message.edit_text(test.full_info(), reply_markup=begin_kb(test_pk))

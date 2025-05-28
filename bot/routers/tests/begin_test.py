import asyncio

from aiogram import Router, types, F, Bot
from aiogram.types import CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _

from bot.functions.send_test import test_sender
from Test.models import Test, Task
from Admin.models import User

router = Router(name=__name__)


def test_role():
    kb = [
        [
            KeyboardButton(text=str(_("Stop"))),
            KeyboardButton(text=str(_("Next"))),
        ]
    ]

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


async def are_you_ready(call: CallbackQuery):
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        ...
    try:
        msg = await call.message.answer(str(_("Are you ready?")))
        await asyncio.sleep(1)
        await msg.edit_text(str(_("Let's go!")))
        await asyncio.sleep(1)
        await msg.delete()
        await call.message.answer(str(_("Test started!")), reply_markup=test_role())
    except:
        ...


@router.callback_query(F.data.startswith("begin:"))
async def begin(call: types.CallbackQuery, user: User, bot: Bot):
    test_pk = int(call.data.split(":")[1])
    test = Test.objects.get(pk=test_pk)

    task = Task.objects.create_for_user(user)
    task.add_questions(*test.questions.all())

    try:
        task.start()
    except IntegrityError as e:
        await call.message.answer(
            str(_("The test has already started.\n\nStop it with the /stop command."))
        )
    else:
        await are_you_ready(call)
        await test_sender(task, bot)

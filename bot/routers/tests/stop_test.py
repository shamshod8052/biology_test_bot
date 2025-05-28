import asyncio

from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.utils.translation import gettext_lazy as _

from bot.filters.multilang_utils import get_translations
from bot.functions.send_statistics import statistics_sender
from Test.models import Task

router = Router()
lock = asyncio.Lock()


@router.message(Command('stop'))
@router.message(F.text.in_(get_translations("Stop")))
async def test_stop(message: Message, bot: Bot, state: FSMContext):
    async with lock:
        await state.clear()
        try:
            task = Task.objects.get(chat__telegram_id=message.chat.id, is_started=True)
        except Task.DoesNotExist:
            await message.reply(str(_("Test not set")))
            return
        await task.stop_poll(bot)
        task.stop()
        await statistics_sender(task, bot)


@router.callback_query(F.data == 'stop_quiz')
async def call_stop(call: CallbackQuery, bot: Bot):
    async with lock:
        try:
            task = Task.objects.get(chat__telegram_id=call.message.chat.id, is_started=True)
        except Task.DoesNotExist:
            await call.message.reply(str(_("Test not set")))
            return
        await task.stop_poll(bot)
        task.stop()
        await call.message.edit_reply_markup(reply_markup=None)
        await statistics_sender(task, bot)

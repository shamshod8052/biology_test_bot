import asyncio

from aiogram import F, Bot, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from django.utils.translation import gettext_lazy as _

from bot.filters.multilang_utils import get_translations
from bot.functions.send_test import test_sender
from Test.models import Task

router = Router()
lock = asyncio.Lock()


@router.message(Command("next"))
@router.message(F.text.in_(get_translations("Next")))
async def get_next_test(message: Message, bot: Bot):
    async with lock:
        try:
            task = Task.objects.get(chat__telegram_id=message.chat.id, is_started=True)
        except Task.DoesNotExist:
            await message.reply(str(_("Test not set")))
            return
        await task.stop_poll(bot)
        if task.last_quest:
            task.last_quest.set_answered()
        await test_sender(task, bot)


@router.callback_query(F.data == 'resume_quiz')
async def send_next_question(call: CallbackQuery, bot: Bot):
    async with lock:
        try:
            task = Task.objects.get(chat__telegram_id=call.message.chat.id, is_started=True)
        except Task.DoesNotExist:
            await call.message.reply(str(_("Test not set")))
            return
        if task.last_quest:
            task.last_quest.set_answered()
        await call.message.edit_reply_markup(reply_markup=None)
        await test_sender(task, bot)

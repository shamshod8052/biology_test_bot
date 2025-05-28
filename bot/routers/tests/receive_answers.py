from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, PollAnswer

from Test.models import Task
from bot.functions.send_test import test_sender
from bot.keyboards.tests import inline_test_kb, edit_inline_kb

router = Router(name=__name__)


@router.poll_answer()
async def check_for_poll(poll: PollAnswer, bot: Bot):
    poll_id = poll.poll_id
    ans = poll.option_ids[0]
    user_id = poll.user.id
    full_name = poll.user.full_name
    username = poll.user.username
    try:
        task = Task.objects.get(poll_id=poll_id)
    except Task.DoesNotExist:
        return
    if not task.is_started:
        return
    task.add_points4gamer(user_id, full_name, username, ans)
    task.last_quest.set_answered()

    await test_sender(task, bot)


@router.callback_query(F.data.startswith('inline_ans:'))
async def check_for_poll(call: CallbackQuery, bot: Bot):
    ans = int(call.data.split(':')[1])
    user_id = call.from_user.id
    full_name = call.from_user.full_name
    username = call.from_user.username
    try:
        task = Task.objects.get(chat__telegram_id=call.message.chat.id, is_started=True)
    except Task.DoesNotExist:
        return
    if not task.is_started:
        return
    await call.message.edit_reply_markup(
        inline_message_id=call.inline_message_id,
        reply_markup=edit_inline_kb(call.message.reply_markup, task.last_quest.question, ans)
    )
    task.add_points4gamer(user_id, full_name, username, ans)
    task.last_quest.set_answered()

    await test_sender(task, bot)

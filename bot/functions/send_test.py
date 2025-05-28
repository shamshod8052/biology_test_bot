import asyncio
import time
from typing import Union, Dict, Any, List

from aiogram import Bot
from aiogram.types import InputMediaPhoto, Message
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from bot.functions.send_statistics import statistics_sender
from bot.keyboards.tests import inline_test_kb
from bot.keyboards.tests import test_paused
from Test.models import Quest, Task, Test


async def send_media(question, bot: Bot, chat_id: Union[int, str]):
    if question.photos.exists():
        media = [InputMediaPhoto(media=p.file_id) for p in question.photos.all()]
        await bot.send_media_group(chat_id=chat_id, media=media, protect_content=question.test.protect_content)


async def overflow(question, bot: Bot, chat_id: Union[int, str], prompt: str, options: List[str]) -> Any:
    lines, labels = '', []
    for i, opt in enumerate(options):
        label = chr(65 + i)
        labels.append(label)
        lines += f"\n<b>{label}</b>. <i>{opt}</i>"
    await bot.send_message(chat_id, f"{prompt}\n{lines}", protect_content=question.test.protect_content)
    return str(_('Select!')), labels


async def send_quiz(question, bot: Bot, chat_id: Union[int, str], position: int, total: int) -> Dict[str, Any]:
    prompt = f"[{position}/{total}] {question.text}"
    answers = question.get_answers()
    options = [a.text for a in answers]
    correct_idx = options.index(question.options.filter(is_correct=True).first().text)
    await send_media(question, bot, chat_id)
    if len(prompt) > 200 or any(len(opt) > 100 for opt in options):
        prompt, options = await overflow(question, bot, chat_id, prompt, options)
    msg: Message = await bot.send_poll(
        chat_id=chat_id,
        question=prompt,
        options=options,
        type='quiz',
        is_anonymous=False,
        correct_option_id=correct_idx,
        open_period=question.time_limit,
        protect_content=question.test.protect_content,
        explanation=question.explanation or None,
    )
    return {'poll_id': msg.poll.id, 'message_id': msg.message_id, 'correct_id': correct_idx}


async def send_inline(question, bot: Bot, chat_id: Union[int, str], position: int, total: int) -> Dict[str, Any]:
    prompt = f"[{position}/{total}] {question.text}"
    kb, correct_idx = inline_test_kb(question)
    await send_media(question, bot, chat_id)
    await bot.send_message(
        chat_id, prompt,
        reply_markup=kb,
        protect_content=question.test.protect_content,
        disable_web_page_preview=True
    )
    return {'correct_id': correct_idx}


async def send(
        question, bot: Bot, chat_id: Union[int, str],
        quest_order: int, all_questions_num: int
):
    if question.test.type == Test.Type.QUIZ:
        return await send_quiz(question, bot, chat_id, quest_order, all_questions_num)
    elif question.test.type == Test.Type.INLINE:
        return await send_inline(question, bot, chat_id, quest_order, all_questions_num)

    return ValueError("Unspecified type entered")


async def test_sender(task: Task, bot: Bot, n=1) -> None:
    try:
        quest = task.get_next()
    except ValueError:
        task.stop()
        return await statistics_sender(task, bot)
    position = task.quests.filter(~Q(status=Quest.Status.NOTSET)).count() + 1
    total = task.quests.count()
    meta = await send(quest.question, bot, task.chat.telegram_id, position, total)
    poll_id = meta.get('poll_id')
    task.poll_id = poll_id
    task.save()
    meta['sent_time'] = time.time()
    quest.meta = meta
    quest.status = Quest.Status.PENDING
    quest.save()

    if task.test.type != task.test.Type.QUIZ:
        return
    await asyncio.sleep(task.last_quest.question.time_limit + 1)
    try:
        task.refresh_from_db()
    except Task.DoesNotExist:
        return
    if not task.is_started:
        return
    if task.poll_id == poll_id:
        task.last_quest.set_answered()
        if n >= 2:
            await bot.send_message(task.chat.telegram_id, str(_("Test pauzed!")), reply_markup=test_paused())
            return
        return await test_sender(task, bot, n + 1)
    return

from aiogram import Bot
from django.utils.translation import gettext_lazy as _

from bot.keyboards.main_menus import main_menu_kb
from bot.keyboards.tests import re_start_test_kb
from helpers.time_string import seconds_to_text
from Test.models import Participant, Quest, Task


async def statistics_sender(task: Task, bot: Bot) -> None:
    participant: Participant = task.participants.first()
    if not participant:
        summary = str(_("Mavjud emas!"))
    else:
        all_quests = task.quests.count()
        answered_quests = task.quests.filter(status=Quest.Status.ANSWERED).count()
        summary = _(
            "🏁 \"{topic}\" test the end.\n"
            "\n"
            "♻️ All questions: {all_quests}\n"
            "🟢 Answered: {answered_quests}\n"
            "\n"
            "✅ Correct: {correct}\n"
            "❌ Wrong: {incorrect}\n"
            "⌛️ Skipp: {skipp}\n"
            "⏱️ {time}"
        ).format(
            topic=task.test.name,
            all_quests=all_quests,
            answered_quests=answered_quests,
            correct=participant.correct,
            incorrect=participant.incorrect,
            skipp=answered_quests - participant.correct - participant.incorrect,
            time=seconds_to_text(participant.time_spent),
        )
    await bot.send_message(
        task.chat.telegram_id, summary,
        reply_markup=main_menu_kb()
    )
    await bot.send_message(
        task.chat.telegram_id, str(_("{topic}\n\n⏳ Restart!")).format(topic=task.test.name),
        reply_markup=re_start_test_kb(task.test.pk)
    )

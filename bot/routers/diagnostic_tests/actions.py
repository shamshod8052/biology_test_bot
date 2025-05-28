from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from Admin.models import User
from Certificate.models import DiagnosticTest
from bot.filters.states import TestState
from bot.keyboards.diagnostic_tests import diagnostic_test_kb

router = Router(name=__name__)


@router.callback_query(F.data.startswith('diag_test:'))
@router.callback_query(F.data.startswith('begin_diag_test:'))
async def certificate_diagnostic_func(call: CallbackQuery, user: User):
    test_pk = int(call.data.split(':')[1])
    test = DiagnosticTest.objects.get(pk=test_pk)
    if not test.is_active:
        return await call.answer(str(_("This test is not active!")), show_alert=True)
    if 'begin_diag_test:' in call.data:
        if not test.is_view():
            return await call.answer(str(_("Please wait for the test start time!")), show_alert=True)
        test.add_user_answers(user, '', False)
        if test.started_at and test.ends_at:
            await call.answer(str(_("The testing process has begun!")), show_alert=True)
    text = (
        "<b>{name}</b>"
        "{description}"
    ).format(
        name=test.name,
        description=test.get_description(),
    )

    keyboard = diagnostic_test_kb(test, user)

    await call.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)


@router.callback_query(F.data.startswith('get_quests_file:'))
async def get_quests_file_func(call: CallbackQuery):
    test_pk = int(call.data.split(':')[1])
    test = DiagnosticTest.objects.get(pk=test_pk)
    if not test.is_active:
        return await call.answer(str(_("This test is not active!")), show_alert=True)
    await call.answer()
    await call.message.answer_document(document=test.tg_file_id)


@router.callback_query(F.data.startswith('check_answers:'))
async def check_answers_func(call: CallbackQuery, user: User, state: FSMContext):
    test_pk = int(call.data.split(':')[1])
    test = DiagnosticTest.objects.get(pk=test_pk)
    if not test.is_active:
        return await call.answer(str(_("This test is not active!")), show_alert=True)
    if test.is_answered(user):
        await call.message.edit_reply_markup(reply_markup=diagnostic_test_kb(test, user))
        return await call.answer(str(_("You have already answered!")), show_alert=True)
    if test.is_end():
        return await call.answer(str(_("The time to submit answers is over!")), show_alert=True)
    await state.set_state(TestState.check_answers)
    await call.answer()
    await state.update_data({'checking_test_id': test_pk})
    text = str(_(
        f"Enter your answers as in the following example:\n\n"
        f"abdcad...\n"
        f"45\n"
        f"school\n"
        f"23.4\n\n"
        f"That is, first the closed test answers in one row, then the closed test answers in separate rows!"
    ))
    await call.message.answer(text=text)


@router.message(TestState.check_answers)
async def answer_checker(message: Message, user: User, state: FSMContext):
    data = await state.get_data()
    test_pk = data.get('checking_test_id')
    test = DiagnosticTest.objects.get(pk=test_pk)
    try:
        test.add_user_answers(user, message.text)
    except ValidationError as e:
        await message.answer(text=str(_("Invalid answers! Try again...")))
    else:
        await state.clear()
        await message.answer(text=str(_("Your answers have been accepted!")))
        user_answer = test.user_answers.filter(user=user).first()
        if not (user_answer and user_answer.answers_text):
            text = str(_("Not found!"))
        else:
            text = user_answer.get_result_text()
        await message.reply(text=text)


@router.callback_query(F.data.startswith('view_answers:'))
async def view_answers_func(call: CallbackQuery, user: User):
    test_pk = int(call.data.split(':')[1])
    test = DiagnosticTest.objects.get(pk=test_pk)
    if not test.is_active:
        return await call.answer(str(_("This test is not active!")), show_alert=True)
    if not test.is_answered(user):
        return await call.answer(str(_("You haven't sent your answers yet!")), show_alert=True)
    await call.answer()
    user_answer = test.user_answers.filter(user=user).first()
    if not (user_answer and user_answer.answers_text):
        text = str(_("Not found!"))
    else:
        text = user_answer.get_result_text()
    await call.message.reply(text=text)

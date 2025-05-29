from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from django.utils.translation import gettext as _

from Knowledge.models import BaseLesson, Status
from bot.filters.multilang_utils import get_translations
from bot.filters.states import Keyboard
from bot.functions.objects_to_text import get_objects_text
from bot.keyboards.video_lessons import video_lessons_kb

router = Router(name=__name__)


@router.message(F.text.in_(get_translations("Video lessons")))
@router.message(F.text.in_(get_translations("Test analyses")), Keyboard.certificate)
@router.message(F.text.in_(get_translations("Test analyses")), Keyboard.attestation)
async def video_lessons_func(message: Message, state: FSMContext):
    st = await state.get_state()
    if st == 'Keyboard:certificate':
        status = Status.CERTIFICATE
    elif st == 'Keyboard:attestation':
        status = Status.ATTESTATION
    else:
        status = Status.NOTSET
    await state.update_data({'status': status})
    rows_num, column_num = 5, 1
    queryset = BaseLesson.objects.filter(status=status, is_active=True).all()
    text = get_objects_text(queryset, 'name', rows_num * column_num)
    if not text:
        await message.answer(_("No lessons found!"))
        return
    await message.answer(
        text=text, reply_markup=video_lessons_kb(status, rows_num=rows_num, column_num=column_num)
    )

@router.callback_query(F.data.startswith("page_lr_lesson:"))
async def lesson_page(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    status = data.get('status')
    page_num = int(call.data.split(":")[1])
    rows_num, column_num = 5, 1
    queryset = BaseLesson.objects.filter(status=status, is_active=True).all()
    text = get_objects_text(queryset, 'name', rows_num * column_num, page_num)
    await call.message.edit_text(
        text=text, reply_markup=video_lessons_kb(status, page_num)
    )

@router.callback_query(F.data.startswith("lesson:"))
async def get_lesson(call: types.CallbackQuery):
    lesson_id = int(call.data.split(":")[1])
    lesson = BaseLesson.objects.get(id=lesson_id)
    await call.answer()
    await call.message.answer_video(
        video=lesson.file_id,
        caption=lesson.description,
        protect_content=lesson.protect_content
    )

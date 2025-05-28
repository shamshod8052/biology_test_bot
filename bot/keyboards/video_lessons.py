from itertools import islice

from aiogram.types import InlineKeyboardButton
from django.utils.translation import gettext_lazy as _

from Knowledge.models import BaseLesson, Status
from bot.keyboards.keyboard_paginator import BackButton, Paginator


def video_lessons_kb(status: Status, page_num=1, rows_num=2, column_num=3):
    queryset = BaseLesson.objects.filter(status=status, is_active=True).all()
    rows_list = [
        InlineKeyboardButton(text=f"{n + 1}", callback_data=f"lesson:{lesson.pk}")
        for n, lesson in enumerate(queryset)
    ]
    it = iter(rows_list)
    rows_list = iter(lambda: tuple(islice(it, column_num)), ())

    back_obj = BackButton(str(_("Main menu")), "main_menu")
    paginator = Paginator(list(rows_list), rows_num, back_obj, True, True)

    return paginator.get_page(page_num, 'lr_lesson').as_markup()

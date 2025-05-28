from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext_lazy as _

from Certificate.models import DiagnosticTest
from bot.keyboards.keyboard_paginator import Paginator


def diag_tests(page_num, per_page=5):
    queryset = DiagnosticTest.objects.filter(is_active=True).all()
    rows_list = [
        [
            InlineKeyboardButton(text=f"{n + 1}", callback_data=f"diag_test:{test.pk}")
        ] for n, test in enumerate(queryset) if test.is_active
    ]

    # back_obj = BackButton()
    paginator = Paginator(rows_list=rows_list, per_page=per_page, circular=True, show_first_last=True)

    return paginator.get_page(page_num, 'diag_test').as_markup()

def diagnostic_test_kb(test, user):
    buttons = []

    user_answer = test.user_answers.filter(user=user).first()
    if not user_answer:
        buttons.append(
            [
                InlineKeyboardButton(text=str(_("Begin")), callback_data=f"begin_diag_test:{test.pk}")
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(text=str(_("Get questions file")), callback_data=f"get_quests_file:{test.id}")
            ]
        )
        is_answered = test.is_answered(user)
        if not is_answered:
            buttons.append(
                [
                    InlineKeyboardButton(text=str(_("Check answers")), callback_data=f"check_answers:{test.id}")
                ]
            )
        if is_answered:
            buttons.append(
                [
                    InlineKeyboardButton(text=str(_("View my answers")), callback_data=f"view_answers:{test.id}")
                ]
            )
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    return markup

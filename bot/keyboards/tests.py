from itertools import islice

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext_lazy as _

from Test.models import Question, Title
from bot.keyboards.keyboard_paginator import BackButton, Paginator


def test_titles_kb(page_num=1):
    queryset = Title.objects.filter(is_active=True).all()
    rows_list = [
        [
            InlineKeyboardButton(text=test.name, callback_data=f"title:{test.pk}")
        ] for test in queryset
    ]

    back_obj = BackButton(str(_("Main menu")), "main_menu")
    paginator = Paginator(rows_list, 5, back_obj, True, True)

    return paginator.get_page(page_num, 'lr_title').as_markup()


def title_tests_kb(title_pk, page_num=1):
    queryset = Title.objects.get(pk=title_pk).tests.filter(is_active=True).all()
    rows_list = [
        [
            InlineKeyboardButton(text=test.name, callback_data=f"test:{test.pk}")
        ] for test in queryset
    ]

    back_obj = BackButton(str(_("Back")), "back2titles")
    paginator = Paginator(rows_list, 5, back_obj, True, True)

    return paginator.get_page(page_num, f"title:{title_pk}").as_markup()


def begin_kb(test_pk: int):
    keyboards = [
        [
            InlineKeyboardButton(text=str(_("Begin")), callback_data=f"begin:{test_pk}"),
        ]
    ]

    kb_markup = InlineKeyboardMarkup(inline_keyboard=keyboards)

    return kb_markup

def re_start_test_kb(test_pk: int):
    kb = [
        [
            InlineKeyboardButton(text=str(_("Restart")), callback_data=f"begin:{test_pk}"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def inline_test_kb(question: Question, selected_id: int = -1):
    answers = question.get_answers()
    correct_idx = question.options.filter(is_correct=True).first().pk

    buttons, size = [], 2
    for option in answers:
        extra = ''
        if selected_id != -1 and question.test.show_answer:
            extra = '✅ ' if option.is_correct else '❌ ' if option.pk == selected_id else ''
        text = f"{extra}{option.text}"
        buttons.append(
            InlineKeyboardButton(text=text, callback_data=f"inline_ans:{option.pk}")
        )
        if len(text) > 25:
            size = 1
    it = iter(buttons)
    inline_keyboard = list(iter(lambda: list(islice(it, size)), []))

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    return keyboard, correct_idx


def edit_inline_kb(reply_markup: InlineKeyboardMarkup, question: Question, selected_id: int = -1):
    correct_idx = question.options.filter(is_correct=True).first().pk

    for rows in reply_markup.inline_keyboard:
        for button in rows:
            extra = ''
            if selected_id != -1 and question.test.show_answer:
                option_id = int(button.callback_data.split(':')[1])
                extra = '✅ ' if option_id == correct_idx else '❌ ' if option_id == selected_id else ''
            button.text = extra + button.text

    return reply_markup


def test_paused():
    kb = [
        [
            InlineKeyboardButton(text=str(_("Resume quiz")), callback_data='resume_quiz'),
        ],
        [
            InlineKeyboardButton(text=str(_("Stop quiz")), callback_data='stop_quiz'),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard

import math
from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext_lazy as _


class BackButton:
    def __init__(self, text: str = str(_("🔙 Back")), callback_data: str = "back"):
        self.text = text
        self.callback_data = callback_data

    def as_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=self.text, callback_data=self.callback_data)

class Page:
    def __init__(self, rows_list, number, prefix, paginator):
        self.rows_list = rows_list
        self.number = number
        self.prefix = prefix
        self.paginator = paginator

    def as_markup(self):
        kb = self.rows_list
        kb.append(self.get_nav_row())
        return InlineKeyboardMarkup(inline_keyboard=kb)

    def get_nav_row(self):
        buttons = []

        if self.has_previous():
            if self.paginator.show_first_last and self.number != self.first_page_number:
                buttons.append(
                    InlineKeyboardButton(text="⏪", callback_data=f"page_{self.prefix}:{self.first_page_number}")
                )
            buttons.append(
                InlineKeyboardButton(text="⬅️", callback_data=f"page_{self.prefix}:{self.previous_page_number()}")
            )

        if self.paginator.back_obj:
            buttons.append(self.paginator.back_obj.as_button())

        if self.has_next():
            buttons.append(
                InlineKeyboardButton(text="➡️", callback_data=f"page_{self.prefix}:{self.next_page_number()}")
            )
            if self.paginator.show_first_last and self.number != self.last_page_number:
                buttons.append(
                    InlineKeyboardButton(text="⏩", callback_data=f"page_{self.prefix}:{self.last_page_number}")
                )

        return buttons

    def has_previous(self):
        return self.number > 1 or (self.paginator.circular if self.paginator.num_pages > 1 else False)

    def has_next(self):
        return (self.number < self.paginator.num_pages or self.paginator.circular) if self.paginator.num_pages > 1 else False

    def previous_page_number(self):
        if self.number <= 1:
            return self.paginator.num_pages if self.paginator.circular else self.number
        return self.number - 1

    def next_page_number(self):
        if self.number >= self.paginator.num_pages:
            return 1 if self.paginator.circular else self.number
        return self.number + 1

    @property
    def first_page_number(self):
        return 1

    @property
    def last_page_number(self):
        return self.paginator.num_pages


class Paginator:
    def __init__(
            self,
            rows_list,
            per_page=5,
            back_obj: Optional[BackButton] = None,
            circular=False,
            show_first_last=False
    ):
        self.rows_list = rows_list
        self.per_page = per_page
        self.back_obj = back_obj
        self.circular = circular
        self.show_first_last = show_first_last

        self.count = len(rows_list)
        self.num_pages = math.ceil(self.count / self.per_page)

    def get_page(self, number, prefix=''):
        start = (number - 1) * self.per_page
        end = start + self.per_page
        
        return Page(self.rows_list[start:end], number, prefix, self)

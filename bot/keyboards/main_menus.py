from aiogram.types import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

from django.utils.translation import gettext_lazy as _


def main_menu_kb():
    keyboards = [
        [
            KeyboardButton(text=str(_("Tests"))),
            KeyboardButton(text=str(_("Video lessons"))),
        ],
        [
            KeyboardButton(text=str(_("Attestation"))),
            KeyboardButton(text=str(_("Certificate"))),
        ],
    ]

    kb_markup = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)

    return kb_markup


def attestation_menu_kb():
    keyboards = [
        [
            KeyboardButton(text=str(_("Diagnostic tests"))),
            KeyboardButton(text=str(_("Test analyses"))),
        ],
        [
            KeyboardButton(text=str(_("Attestation courses"))),
            KeyboardButton(text=str(_("Subscribe"))),
        ],
        [
            KeyboardButton(text=str(_("Main menu"))),
        ],
    ]

    kb_markup = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)

    return kb_markup


def certificate_menu_kb():
    keyboards = [
        [
            KeyboardButton(text=str(_("Diagnostic tests"))),
            KeyboardButton(text=str(_("Test analyses"))),
        ],
        [
            KeyboardButton(text=str(_("Certificate courses"))),
            KeyboardButton(text=str(_("Subscribe"))),
        ],
        [
            KeyboardButton(text=str(_("Main menu"))),
        ],
    ]

    kb_markup = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)

    return kb_markup

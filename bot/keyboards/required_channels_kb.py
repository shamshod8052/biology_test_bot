from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Admin.models import Channel


def get_channels_kb(missing_channels: list[Channel]):
    buttons = [
        [
            InlineKeyboardButton(text=f"{n + 1}. {kb.name}", url=kb.url)
        ] for n, kb in enumerate(missing_channels)
    ]
    kb_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    return kb_markup

from aiogram import F, Router
from aiogram.types import Message
from django.utils.translation import gettext_lazy as _

from bot.filters.multilang_utils import get_translations
from bot.filters.states import Keyboard

router = Router(name=__name__)


@router.message(F.text.in_(get_translations("Subscribe")), Keyboard.attestation)
async def attestation_subscribe(message: Message):
    from Attestation.models import Channel

    extra_text = f"{_('Channels list for subscribe')}"
    channels_text = Channel.objects.get_text()
    text=  f"{extra_text}\n\n{channels_text}"\
        if channels_text \
        else str(_("Channels list not found!"))

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text.in_(get_translations("Subscribe")), Keyboard.certificate)
async def attestation_subscribe(message: Message):
    from Certificate.models import Channel

    extra_text = f"{_('Channels list for subscribe')}"
    channels_text = Channel.objects.get_text()
    text = f"{extra_text}\n\n{channels_text}" \
        if channels_text \
        else str(_("Channels list not found!"))

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text.in_(get_translations("Test analyses")))
@router.message(F.text.in_(get_translations("Subscribe")))
async def subscribe(message: Message):
    await message.answer("👉 /start /start 👈")

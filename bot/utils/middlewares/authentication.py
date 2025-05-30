from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Awaitable, Any
from django.utils.translation import gettext_lazy as _

from Admin.helpers import is_user_subscribed
from Admin.models import User
from bot.keyboards.required_channels_kb import get_channels_kb


class AuthenticationMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
                       event: Update,
                       data: Dict[str, Any]
                       ) -> Any:
        bot_user = data['event_from_user']
        if bot_user is None:
            return await handler(event, data)

        try:
            user = await User.objects.aget(telegram_id=bot_user.id)
        except User.DoesNotExist:
            user = None
        else:
            user.first_name = bot_user.first_name
            user.last_name = bot_user.last_name
            user.username = bot_user.username
            await user.asave()
        data['user'] = user

        is_subscribed, missing_channels = await is_user_subscribed(event.bot, bot_user.id)

        if not is_subscribed:
            text = _("Please subscribe to the following channels:\n\n"
                     "Once subscribed, send the /start command again.")
            channels_kb = get_channels_kb(missing_channels)
            await event.message.answer(str(text), reply_markup=channels_kb)
            return

        return await handler(event, data)

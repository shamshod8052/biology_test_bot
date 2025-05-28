from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Awaitable, Any
from Admin.models import User


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

        return await handler(event, data)

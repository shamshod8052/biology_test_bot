import traceback

from aiogram import Bot
from Admin.models import Channel

async def is_user_subscribed(bot: Bot, user_chat_id: int) -> tuple[bool, list[Channel]]:
    """
    Foydalanuvchining barcha majburiy kanallarga obuna bo‘lganini tekshiradi.
    True bo‘lsa - ruxsat, False bo‘lsa - obuna bo‘lmaganlar ro‘yxati bilan.
    """
    unsubscribed_channels = []
    required_channels = Channel.objects.filter(is_required=True, is_active=True)

    for channel in required_channels:
        try:
            member = await bot.get_chat_member(channel.chat_id, user_chat_id)
            if member.status in ["left", "kicked"]:
                unsubscribed_channels.append(channel)
        except Exception as e:
            ...  # Kanal topilmasa yoki boshqa xato

    return len(unsubscribed_channels) == 0, unsubscribed_channels

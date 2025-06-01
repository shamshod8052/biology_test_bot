import redis
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from django.conf import settings

from bot.errors import router as error_router
from bot.helpers import get_webhook_url
from bot.routers import router as handler_router
from bot.utils.middlewares import authentication, i18n
from bot.utils.storage import DjangoRedisStorage

rd = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

dp = Dispatcher(storage=DjangoRedisStorage())
bot_session = AiohttpSession()

bot = Bot(settings.BOT_TOKEN, session=bot_session, default=DefaultBotProperties(parse_mode='HTML'))

dp.include_router(handler_router)
dp.include_router(error_router)
dp.update.outer_middleware.register(authentication.AuthenticationMiddleware())
dp.update.outer_middleware.register(i18n.I18Middleware())


async def on_startup():
    if settings.DEBUG:
        await bot.delete_webhook()
    else:
        webhook_info = await bot.get_webhook_info()
        webhook_url = get_webhook_url()
        if webhook_url != webhook_info.url:
            await bot.set_webhook(
                url=webhook_url,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=True
            )


async def on_shutdown():
    await bot_session.close()

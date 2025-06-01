from django.conf import settings
from django.core.management import BaseCommand

from bot.misc import dp, bot, on_startup, on_shutdown


class Command(BaseCommand):
    def handle(self, *args, **options):
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        if settings.DEBUG:
            dp.run_polling(bot)

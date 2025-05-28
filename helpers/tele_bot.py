from django.conf import settings
from telebot import TeleBot

tele_bot = TeleBot(settings.BOT_TOKEN)

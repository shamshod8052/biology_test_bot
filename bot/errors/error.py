from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.types.error_event import ErrorEvent

from main.settings import ADMINS

router = Router()


# Define a reusable function to check exception messages
def is_exception(exception: Exception, phrases: list[str]) -> bool:
    """Check if the exception message contains any of the ignored phrases."""
    exception_message = str(exception)
    return any(phrase in exception_message for phrase in phrases)

@router.error(F.update.message.as_("message"))
async def handle_message_exception(event: ErrorEvent, message: Message, bot: Bot):
    exceptions = '\n\n'.join(event.exception.args)
    text = f"ID: {message.from_user.id}\n\n{exceptions}"

    await bot.send_message(chat_id=ADMINS[0], text=text)

@router.error(F.update.callback_query.as_("call"))
async def handle_callback_exception(event: ErrorEvent, call: CallbackQuery, bot: Bot):
    exceptions = '\n\n'.join(event.exception.args)
    text = f"ID: {call.from_user.id}\n\n{exceptions}"

    await bot.send_message(chat_id=ADMINS[0], text=text)
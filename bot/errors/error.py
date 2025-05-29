import traceback

from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery

from main.settings import ADMINS

router = Router()


# Define a reusable function to check exception messages
def is_exception(exception: Exception, phrases: list[str]) -> bool:
    """Check if the exception message contains any of the ignored phrases."""
    exception_message = str(exception)
    return any(phrase in exception_message for phrase in phrases)

@router.error(F.update.message.as_("message"))
async def handle_message_exception(message: Message, bot: Bot):
    text = f"ID: {message.from_user.id}\n\n{traceback.format_exc()}"
    for t in range(0, len(text), 4096):
        await bot.send_message(
            chat_id=ADMINS[0],
            text=text[t:t+4096]
        )

@router.error(F.update.callback_query.as_("call"))
async def handle_callback_exception(call: CallbackQuery, bot: Bot):
    text = f"ID: {call.from_user.id}\n\n{traceback.format_exc()}"
    for t in range(0, len(text), 4096):
        await bot.send_message(
            chat_id=ADMINS[0],
            text=text[t:t + 4096]
        )

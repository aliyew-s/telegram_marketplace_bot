from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.language import language_keyboard
from app.keyboards.main_menu import main_menu_keyboard
from app.locales.translator import t
from app.services.user import user_service


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    user, _ = await user_service.get_or_create(
        message.from_user
    )

    if user.language:
        await message.answer(
            t("main_menu_text", user.language),
            reply_markup=main_menu_keyboard(
                user.language
            ),
        )
        return

    await message.answer(
        f"{t('welcome')}\n\n"
        f"{t('choose_language')}",
        reply_markup=language_keyboard(),
    )
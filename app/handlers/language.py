from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.main_menu import main_menu_keyboard
from app.services.user import user_service
from app.locales.translator import t


router = Router()


@router.callback_query(
    F.data.startswith("lang:")
)
async def language_handler(
    callback: CallbackQuery,
):
    language = callback.data.split(":", 1)[1]

    await user_service.set_language(
        telegram_id=callback.from_user.id,
        language=language,
    )

    await callback.message.edit_text(
        t("main_menu_text", language),
        reply_markup=main_menu_keyboard(language),
    )   

    await callback.answer()
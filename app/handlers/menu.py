from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.navigation import back_keyboard
from app.keyboards.language import language_keyboard
from app.keyboards.main_menu import main_menu_keyboard
from app.locales.translator import t
from app.services.user import user_service


router = Router()


@router.callback_query(F.data == "language")
async def language_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    await callback.message.edit_text(
        t("choose_language", language),
        reply_markup=language_keyboard(),
    )

    await callback.answer()


@router.callback_query(
    F.data.in_(
        {
            "search",
            "my_groups",
            "favorites",
            "channel",
        }
    )
)
async def not_implemented_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    await callback.answer(
        t("not_implemented", language)
    )


@router.callback_query(F.data == "help")
async def help_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    await callback.message.edit_text(
        f"🆘 <b>{t('help', language)}</b>\n\n"
        f"{t('help_text', language)}",
        reply_markup=back_keyboard(language),
    )

    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    await callback.message.edit_text(
        t("main_menu", language),
        reply_markup=main_menu_keyboard(
            language
        ),
    )

    await callback.answer()
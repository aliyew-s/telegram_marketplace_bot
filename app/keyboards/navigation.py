from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.locales.translator import t


def back_keyboard(
    language: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("back", language),
                    callback_data="back_to_menu",
                ),
            ],
        ]
    )
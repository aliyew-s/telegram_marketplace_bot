from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.locales.translator import t


def main_menu_keyboard(
    language: str = "ru",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("search", language),
                    callback_data="search",
                ),
                InlineKeyboardButton(
                    text=t("my_groups", language),
                    callback_data="my_groups",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("favorites", language),
                    callback_data="favorites",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("channel", language),
                    callback_data="channel",
                ),
                InlineKeyboardButton(
                    text=t("help", language),
                    callback_data="help",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("language", language),
                    callback_data="language",
                ),
            ],
        ]
    )
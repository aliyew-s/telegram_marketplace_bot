from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def add_group_keyboard(
    language: str,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить группу",
                    callback_data="add_group",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_to_menu",
                )
            ],
        ]
    )
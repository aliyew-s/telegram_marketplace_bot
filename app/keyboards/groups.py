from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


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


def my_groups_keyboard(
    current_index: int,
    total_groups: int,
) -> InlineKeyboardMarkup:
    navigation_buttons = []

    if current_index > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=(
                    f"group_page:{current_index - 1}"
                ),
            )
        )

    navigation_buttons.append(
        InlineKeyboardButton(
            text=f"{current_index + 1}/{total_groups}",
            callback_data="group_page_current",
        )
    )

    if current_index < total_groups - 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=(
                    f"group_page:{current_index + 1}"
                ),
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            navigation_buttons,
            [
                InlineKeyboardButton(
                    text="➕ Добавить группу",
                    callback_data="add_group",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="back_to_menu",
                )
            ],
        ]
    )
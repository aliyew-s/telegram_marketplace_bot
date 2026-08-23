import os
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from app.states.groups import AddGroupStates

from app.keyboards.navigation import back_keyboard
from app.keyboards.language import language_keyboard
from app.keyboards.main_menu import main_menu_keyboard
from app.keyboards.groups import add_group_keyboard
from app.locales.translator import t

from app.services.telegram_group import telegram_group_service
from app.services.user import user_service
from app.services.group import group_service


router = Router()


def group_result_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Мои группы",
                    callback_data="my_groups",
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


def my_group_keyboard():
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
                    text="🏠 Главное меню",
                    callback_data="back_to_menu",
                )
            ],
        ]
    )


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


@router.callback_query(F.data == "my_groups")
async def my_groups_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    user = await user_service.get_or_create(
        callback.from_user
    )

    db_user, _ = user

    group = await group_service.get_by_owner_id(
        db_user.id
    )

    if group is None:
        await callback.message.edit_text(
            "👥 <b>Мои группы</b>\n\n"
            "У вас пока нет добавленных групп.",
            reply_markup=add_group_keyboard(language),
        )

        await callback.answer()
        return

    text = (
        "👥 <b>Моя группа</b>\n\n"
        f"📌 <b>Название:</b> {group.name}\n"
        f"👥 <b>Участников:</b> {group.participants_count}\n"
        f"📊 <b>Статус:</b> {group.status}\n"
    )

    if group.username:
        text += (
            f"🔗 <b>Username:</b> @{group.username}\n"
        )

    if group.description:
        text += (
            f"\n📝 <b>Описание:</b>\n"
            f"{group.description}\n"
        )

    if group.avatar:
        avatar_path = (
            await telegram_group_service.download_avatar(
                bot=callback.bot,
                file_id=group.avatar,
            )
        )

        if avatar_path:
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

            photo = FSInputFile(avatar_path)

            await callback.message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=my_group_keyboard(),
            )

            os.remove(avatar_path)
        else:
            await callback.message.edit_text(
                text,
                reply_markup=my_group_keyboard(),
            )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=my_group_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == "add_group")
async def add_group_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    await state.set_state(
        AddGroupStates.waiting_for_link
    )

    await callback.message.edit_text(
        "➕ <b>Добавление группы</b>\n\n"
        "1️⃣ Добавьте бота в группу.\n"
        "2️⃣ Назначьте бота администратором.\n\n"
        "После этого отправьте ссылку.",
        reply_markup=back_keyboard(language),
    )

    await callback.answer()


@router.message(AddGroupStates.waiting_for_link)
async def group_link_handler(
    message: Message,
    state: FSMContext,
):
    link = message.text

    language = await user_service.get_language(
        message.from_user.id
    )

    if not link:
        await message.answer(
            "❌ Отправьте ссылку.",
            reply_markup=back_keyboard(language),
        )
        return

    is_valid = telegram_group_service.validate_link(
        link
    )

    if not is_valid:
        await message.answer(
            "❌ Неверная ссылка.",
            reply_markup=back_keyboard(language),
        )
        return

    chat = await telegram_group_service.get_chat(
        bot=message.bot,
        link=link,
    )

    if chat is None:
        await message.answer(
            "❌ Группа не найдена.\n\n"
            "Если группа приватная — сделайте её публичной.",
            reply_markup=back_keyboard(language),
        )
        return

    bot_is_admin = (
        await telegram_group_service.is_bot_admin(
            bot=message.bot,
            chat_id=chat["id"],
        )
    )

    if not bot_is_admin:
        await message.answer(
            "❌ Добавьте этого бота в группу "
            "и назначьте его администратором.",
            reply_markup=back_keyboard(language),
        )
        return

    is_admin = (
        await telegram_group_service.is_user_admin(
            bot=message.bot,
            chat_id=chat["id"],
            user_id=message.from_user.id,
        )
    )

    if not is_admin:
        await message.answer(
            "❌ Вы не администратор этой группы.",
            reply_markup=back_keyboard(language),
        )
        return

    user = await user_service.get_or_create(
        message.from_user
    )

    db_user, _ = user

    await group_service.create(
        owner_id=db_user.id,
        telegram_chat_id=chat["id"],
        username=chat["username"],
        invite_link=link,
        name=chat["title"],
        description=chat["description"],
        avatar=chat["photo"],
        participants_count=chat["participants_count"],
    )

    if chat["username"]:
        text = (
            "✅ <b>Группа найдена!</b>\n\n"
            f"📌 <b>Название:</b> {chat['title']}\n"
            f"👥 <b>Участников:</b> {chat['participants_count']}\n"
            f"🔗 <b>Username:</b> @{chat['username']}\n\n"
            "Группа сохранена и отправлена на модерацию."
        )
    else:
        text = (
            "✅ <b>Группа найдена!</b>\n\n"
            f"📌 <b>Название:</b> {chat['title']}\n"
            f"👥 <b>Участников:</b> {chat['participants_count']}\n\n"
            "Группа сохранена и отправлена на модерацию."
        )

    await message.answer(
        text,
        reply_markup=group_result_keyboard(),
    )

    await state.clear()


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


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    if callback.message.photo:
        await callback.message.delete()

        await callback.message.answer(
            t("main_menu", language),
            reply_markup=main_menu_keyboard(
                language
            ),
        )
    else:
        await callback.message.edit_text(
            t("main_menu", language),
            reply_markup=main_menu_keyboard(
                language
            ),
        )

    await callback.answer()

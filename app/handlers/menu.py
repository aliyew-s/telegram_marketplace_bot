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
from app.keyboards.groups import (
    add_group_keyboard,
    my_groups_keyboard,
)

from app.locales.translator import t

from app.services.telegram_group import telegram_group_service
from app.services.user import user_service
from app.services.group import group_service


router = Router()


def build_group_text(
    group,
    current_index: int,
    total_groups: int,
    language: str,
) -> str:
    group_number = t(
        "group_number",
        language,
    ).format(
        current=current_index + 1,
        total=total_groups,
    )

    text = (
        f"<b>{group_number}</b>\n\n"
        f"{t('group_name', language)} "
        f"{group.name}\n"
        f"{t('group_members', language)} "
        f"{group.participants_count}\n"
        f"{t('group_status', language)} "
        f"{group.status}\n"
    )

    if group.username:
        text += (
            f"{t('group_username', language)} "
            f"@{group.username}\n"
        )

    if group.description:
        text += (
            f"\n{t('group_description', language)}\n"
            f"{group.description}\n"
        )

    return text


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


async def show_group(
    callback: CallbackQuery,
    groups,
    index: int,
):
    """
    Показывает одну группу с аватаром и навигацией.
    """

    if not groups:
        await callback.message.edit_text(
            "👥 <b>Мои группы</b>\n\n"
            "У вас пока нет добавленных групп.",
            reply_markup=add_group_keyboard(
                await user_service.get_language(
                    callback.from_user.id
                )
            ),
        )

        return

    # Защита от неправильного индекса
    if index < 0:
        index = 0

    if index >= len(groups):
        index = len(groups) - 1

    group = groups[index]

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
                reply_markup=my_groups_keyboard(
                    current_index=index,
                    total_groups=len(groups),
                ),
            )

            try:
                os.remove(avatar_path)
            except OSError:
                pass

            return

    # Если аватара нет
    try:
        await callback.message.edit_text(
            text,
            reply_markup=my_groups_keyboard(
                current_index=index,
                total_groups=len(groups),
            ),
        )
    except TelegramBadRequest:
        # Например, если callback.message оказался фотографией
        try:
            await callback.message.delete()
        except TelegramBadRequest:
            pass

        await callback.message.answer(
            text,
            reply_markup=my_groups_keyboard(
                current_index=index,
                total_groups=len(groups),
            ),
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


async def show_group(
    callback: CallbackQuery,
    groups,
    current_index: int,
    language: str,
):
    group = groups[current_index]

    text = build_group_text(
        group=group,
        current_index=current_index,
        total_groups=len(groups),
        language=language,
    )

    keyboard = my_groups_keyboard(
        current_index=current_index,
        total_groups=len(groups),
    )

    if group.avatar:
        avatar_path = (
            await telegram_group_service.download_avatar(
                bot=callback.bot,
                file_id=group.avatar,
            )
        )
    else:
        avatar_path = (
            telegram_group_service.create_default_avatar(
                group.name
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
            reply_markup=keyboard,
        )

        os.remove(avatar_path)

    else:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
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

    groups = await group_service.get_by_owner_id(
        db_user.id
    )

    if not groups:
        await callback.message.edit_text(
            f"👥 <b>{t('my_groups', language)}</b>\n\n"
            f"{t('my_groups_empty', language)}",
            reply_markup=add_group_keyboard(
                language
            ),
        )

        await callback.answer()
        return

    await show_group(
        callback=callback,
        groups=groups,
        current_index=0,
        language=language,
    )

    await callback.answer()



@router.callback_query(
    F.data.startswith("group_page:")
)
async def group_page_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    user = await user_service.get_or_create(
        callback.from_user
    )

    db_user, _ = user

    groups = await group_service.get_by_owner_id(
        db_user.id
    )

    if not groups:
        await callback.answer()
        return

    current_index = int(
        callback.data.split(":")[1]
    )

    if current_index >= len(groups):
        current_index = len(groups) - 1

    await show_group(
        callback=callback,
        groups=groups,
        current_index=current_index,
        language=language,
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("group_page:")
)
async def group_page_handler(
    callback: CallbackQuery,
):
    user = await user_service.get_or_create(
        callback.from_user
    )

    db_user, _ = user

    groups = await group_service.get_by_owner_id(
        db_user.id
    )

    try:
        index = int(
            callback.data.split(":")[1]
        )
    except (ValueError, IndexError):
        await callback.answer()
        return

    await show_group(
        callback=callback,
        groups=groups,
        index=index,
    )

    await callback.answer()


@router.callback_query(
    F.data == "group_page_current"
)
async def group_page_current_handler(
    callback: CallbackQuery,
):
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

    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    await callback.message.answer(
        "➕ <b>Добавление группы</b>\n\n"
        "1️⃣ Добавьте бота в группу.\n"
        "2️⃣ Назначьте бота администратором.\n\n"
        "После этого отправьте ссылку.",
        reply_markup=back_keyboard(language),
    )

    await callback.answer()


@router.message(
    AddGroupStates.waiting_for_link
)
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
            "Если группа приватная — "
            "сделайте её публичной.",
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
        participants_count=chat[
            "participants_count"
        ],
    )

    if chat["username"]:
        text = (
            "✅ <b>Группа найдена!</b>\n\n"
            f"📌 <b>Название:</b> "
            f"{chat['title']}\n"
            f"👥 <b>Участников:</b> "
            f"{chat['participants_count']}\n"
            f"🔗 <b>Username:</b> "
            f"@{chat['username']}\n\n"
            "Группа сохранена и отправлена "
            "на модерацию."
        )
    else:
        text = (
            "✅ <b>Группа найдена!</b>\n\n"
            f"📌 <b>Название:</b> "
            f"{chat['title']}\n"
            f"👥 <b>Участников:</b> "
            f"{chat['participants_count']}\n\n"
            "Группа сохранена и отправлена "
            "на модерацию."
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
async def back_to_menu_handler(
    callback: CallbackQuery,
):
    language = await user_service.get_language(
        callback.from_user.id
    )

    try:
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
    except TelegramBadRequest:
        pass

    await callback.answer()
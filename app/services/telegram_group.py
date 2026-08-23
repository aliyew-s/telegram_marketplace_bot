from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
)


class TelegramGroupService:

    def validate_link(
        self,
        link: str,
    ) -> bool:
        link = link.strip()

        parsed = urlparse(link)

        if parsed.scheme != "https":
            return False

        if parsed.netloc != "t.me":
            return False

        if not parsed.path or parsed.path == "/":
            return False

        return True

    async def get_chat(
        self,
        bot: Bot,
        link: str,
    ):
        parsed = urlparse(link)

        username = parsed.path.strip("/")

        if username.startswith("+"):
            return None

        if username.startswith("joinchat/"):
            return None

        if not username.startswith("@"):
            username = f"@{username}"

        try:
            chat = await bot.get_chat(username)

            participants_count = (
                await bot.get_chat_member_count(
                    chat.id
                )
            )

            return {
                "id": chat.id,
                "type": chat.type,
                "title": chat.title,
                "username": chat.username,
                "description": chat.description,
                "photo": (
                    chat.photo.big_file_id
                    if chat.photo
                    else None
                ),
                "participants_count": participants_count,
            }

        except (
            TelegramBadRequest,
            TelegramForbiddenError,
        ):
            return None

    async def download_avatar(
        self,
        bot: Bot,
        file_id: str,
    ) -> str | None:
        try:
            file = await bot.get_file(file_id)

            if not file.file_path:
                return None

            with NamedTemporaryFile(
                suffix=".jpg",
                delete=False,
            ) as temp_file:
                file_path = temp_file.name

            await bot.download_file(
                file.file_path,
                destination=file_path,
            )

            return file_path

        except (
            TelegramBadRequest,
            TelegramForbiddenError,
        ):
            return None

    async def is_bot_admin(
        self,
        bot: Bot,
        chat_id: int,
    ) -> bool:
        try:
            bot_user = await bot.me()

            member = await bot.get_chat_member(
                chat_id=chat_id,
                user_id=bot_user.id,
            )

            print(
                "DEBUG BOT STATUS:",
                member.status,
            )

            return member.status in {
                "administrator",
                "creator",
            }

        except (
            TelegramBadRequest,
            TelegramForbiddenError,
        ):
            return False

    async def is_user_admin(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
    ) -> bool:
        try:
            member = await bot.get_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )

            print(
                "DEBUG USER:",
                user_id,
            )

            print(
                "DEBUG CHAT:",
                chat_id,
            )

            print(
                "DEBUG STATUS:",
                member.status,
            )

            return member.status in {
                "creator",
                "administrator",
            }

        except TelegramBadRequest as error:
            print(
                "DEBUG TELEGRAM BAD REQUEST:",
                error,
            )

            return False

        except TelegramForbiddenError as error:
            print(
                "DEBUG TELEGRAM FORBIDDEN:",
                error,
            )

            return False


telegram_group_service = TelegramGroupService()
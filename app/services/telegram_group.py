from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

import hashlib

from PIL import Image, ImageDraw, ImageFont

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
            print("DEBUG AVATAR FILE ID:", file_id)

            file = await bot.get_file(file_id)

            print("DEBUG AVATAR FILE:", file)
            print(
                "DEBUG AVATAR FILE PATH:",
                file.file_path,
            )

            if not file.file_path:
                print("DEBUG: FILE PATH IS NONE")
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

            print(
                "DEBUG AVATAR DOWNLOADED:",
                file_path,
            )

            return file_path

        except (
            TelegramBadRequest,
            TelegramForbiddenError,
        ) as error:
            print(
                "DEBUG AVATAR ERROR:",
                error,
            )
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

            return member.status in {
                "creator",
                "administrator",
            }

        except (
            TelegramBadRequest,
            TelegramForbiddenError,
        ):
            return False

    def create_default_avatar(
        self,
        name: str,
    ) -> str:
        letter = name.strip()[0].upper()

        colors = [
            (66, 133, 244),
            (52, 168, 83),
            (251, 188, 5),
            (234, 67, 53),
            (156, 39, 176),
            (0, 150, 136),
        ]

        hash_value = hashlib.md5(
            name.encode("utf-8")
        ).hexdigest()

        color_index = (
            int(hash_value[:8], 16)
            % len(colors)
        )

        background_color = colors[color_index]

        image = Image.new(
            "RGB",
            (500, 500),
            background_color,
        )

        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc",
                250,
            )
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox(
            (0, 0),
            letter,
            font=font,
        )

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (500 - text_width) / 2
        y = (500 - text_height) / 2 - bbox[1]

        draw.text(
            (x, y),
            letter,
            fill="white",
            font=font,
        )

        with NamedTemporaryFile(
            suffix=".jpg",
            delete=False,
        ) as temp_file:
            file_path = temp_file.name

        image.save(
            file_path,
            format="JPEG",
            quality=90,
        )

        return file_path
        
telegram_group_service = TelegramGroupService()
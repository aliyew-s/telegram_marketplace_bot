from aiogram.types import User as TelegramUser

from app.db.repository import UserRepository
from app.db.session import session_factory


class UserService:
    async def get_or_create(
        self,
        tg_user: TelegramUser,
    ):
        async with session_factory() as session:
            repository = UserRepository(session)

            user = await repository.get_by_telegram_id(
                tg_user.id
            )

            if user is None:
                user = await repository.create(
                    telegram_id=tg_user.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    last_name=tg_user.last_name,
                )

                return user, True

            user = await repository.update_from_telegram(
                user=user,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
            )

            return user, False

    async def set_language(
        self,
        telegram_id: int,
        language: str,
    ):
        async with session_factory() as session:
            repository = UserRepository(session)

            user = await repository.get_by_telegram_id(
                telegram_id
            )

            if user is None:
                return None

            return await repository.set_language(
                user=user,
                language=language,
            )

    async def get_language(
        self,
        telegram_id: int,
    ) -> str:
        async with session_factory() as session:
            repository = UserRepository(session)

            language = await repository.get_language(
                telegram_id
            )

            return language or "ru"


user_service = UserService()
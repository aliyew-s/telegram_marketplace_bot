from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(
        self,
        telegram_id: int,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> User:
        now = datetime.now(timezone.utc)

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            last_interaction_at=now,
        )

        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update_from_telegram(
        self,
        user: User,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> User:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.last_interaction_at = datetime.now(
            timezone.utc
        )

        await self.session.commit()

        return user

    async def set_language(
        self,
        user: User,
        language: str,
    ) -> User:
        user.language = language
        user.last_interaction_at = datetime.now(
            timezone.utc
        )

        await self.session.commit()

        return user


    async def get_language(
        self,
        telegram_id: int,
    ) -> str | None:
        result = await self.session.execute(
            select(User.language).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Group


class GroupRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_owner_id(
        self,
        owner_id: int,
    ) -> list[Group]:
        result = await self.session.execute(
            select(Group)
            .where(
                Group.owner_id == owner_id
            )
            .order_by(
                Group.created_at.desc()
            )
        )

        return list(result.scalars().all())


    async def get_by_id(
        self,
        group_id: int,
    ) -> Group | None:
        result = await self.session.execute(
            select(Group).where(
                Group.id == group_id
            )
        )

        return result.scalar_one_or_none()

    async def get_pending_groups(
        self,
    ) -> list[Group]:
        result = await self.session.execute(
            select(Group)
            .where(
                Group.status == "pending"
            )
            .order_by(
                Group.created_at.asc()
            )
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        group_id: int,
        status: str,
    ) -> Group | None:
        group = await self.get_by_id(group_id)

        if group is None:
            return None

        group.status = status

        await self.session.commit()
        await self.session.refresh(group)

        return group
    

    async def create(
        self,
        owner_id: int,
        telegram_chat_id: int,
        username: str | None,
        invite_link: str,
        name: str,
        description: str | None,
        avatar: str | None,
        participants_count: int,
    ) -> Group:
        group = Group(
            owner_id=owner_id,
            telegram_chat_id=telegram_chat_id,
            username=username,
            invite_link=invite_link,
            name=name,
            description=description,
            avatar=avatar,
            participants_count=participants_count,
            status="pending",
        )

        self.session.add(group)

        await self.session.commit()
        await self.session.refresh(group)

        return group
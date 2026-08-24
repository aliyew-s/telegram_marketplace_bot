from app.db.group_repository import GroupRepository
from app.db.session import session_factory


class GroupService:
    async def get_by_owner_id(
        self,
        owner_id: int,
    ):
        async with session_factory() as session:
            repository = GroupRepository(session)

            return await repository.get_by_owner_id(
                owner_id
            )

    async def get_by_id(
        self,
        group_id: int,
    ):
        async with session_factory() as session:
            repository = GroupRepository(session)

            return await repository.get_by_id(
                group_id
            )

    async def get_pending_groups(self):
        async with session_factory() as session:
            repository = GroupRepository(session)

            return await repository.get_pending_groups()

    async def update_status(
        self,
        group_id: int,
        status: str,
    ):
        async with session_factory() as session:
            repository = GroupRepository(session)

            return await repository.update_status(
                group_id=group_id,
                status=status,
            )

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
    ):
        async with session_factory() as session:
            repository = GroupRepository(session)

            return await repository.create(
                owner_id=owner_id,
                telegram_chat_id=telegram_chat_id,
                username=username,
                invite_link=invite_link,
                name=name,
                description=description,
                avatar=avatar,
                participants_count=participants_count,
            )


group_service = GroupService()
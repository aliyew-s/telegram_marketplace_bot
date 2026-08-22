"""create users table

Revision ID: 0001_create_users
Revises:
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_users"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "telegram_id",
            sa.BigInteger(),
            nullable=False,
        ),

        sa.Column(
            "username",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "first_name",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "last_name",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "language",
            sa.String(5),
            nullable=True,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.Column(
            "last_interaction_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_users_telegram_id",
        "users",
        ["telegram_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_users_telegram_id",
        table_name="users",
    )

    op.drop_table("users")
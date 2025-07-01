"""init users

Revision ID: 3eefdfb80e7b
Revises: 
Create Date: 2025-06-29 14:54:18.237732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3eefdfb80e7b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ───────────────────────────── upgrade ─────────────────────────────
def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1. если таблицы users ещё нет – создаём
    if "users" not in insp.get_table_names():
        op.create_table(
            "users",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(100)),
            sa.Column("surname", sa.String(100)),
            sa.Column("patronymic", sa.String(100)),
            sa.Column("phone", sa.String(20)),
            sa.Column("email", sa.String(150), nullable=False, unique=True),
            sa.Column("password", sa.String(255)),
            sa.Column("avatar", postgresql.BYTEA),
        )
    else:
        # 2. если таблица есть – приводим поля к актуальным типам/nullable
        op.alter_column(
            "users",
            "avatar",
            existing_type=sa.String(),            # если до этого был VARCHAR
            type_=postgresql.BYTEA(),
            existing_nullable=True,
        )
        op.alter_column(
            "users",
            "password",
            existing_type=sa.VARCHAR(length=255),
            nullable=True,
        )

    # 3. индексы (e-mail уникальный, id — обычный)
    idx_names = [i["name"] for i in insp.get_indexes("users")]
    if "ix_users_email" not in idx_names:
        op.create_index("ix_users_email", "users", ["email"], unique=True)
    if "ix_users_id" not in idx_names:
        op.create_index("ix_users_id", "users", ["id"])


# ──────────────────────────── downgrade ────────────────────────────
def downgrade() -> None:
    # при откате достаточно убрать таблицу users и связанные с ней индексы
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

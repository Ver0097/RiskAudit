"""seed admin user

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-01

"""
import bcrypt
from alembic import op
import sqlalchemy as sa

from app.config import get_settings

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """插入默认管理员账号，密码取自配置项 seed_admin_password。"""
    settings = get_settings()
    password_hash = bcrypt.hashpw(
        settings.seed_admin_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    users = sa.table(
        "users",
        sa.column("username", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("display_name", sa.String),
        sa.column("is_admin", sa.Boolean),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        users,
        [
            {
                "username": settings.seed_admin_username,
                "password_hash": password_hash,
                "display_name": "系统管理员",
                "is_admin": True,
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    """回滚：删除该种子管理员账号。"""
    settings = get_settings()
    op.execute(
        sa.text("DELETE FROM users WHERE username = :u").bindparams(
            u=settings.seed_admin_username
        )
    )

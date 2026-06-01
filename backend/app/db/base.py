from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基类，统一元数据用于 Alembic 自动探测。"""
    pass

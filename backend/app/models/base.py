"""
Base ORM model with common columns shared across all tables.
All models should inherit from ModelBase.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ModelBase(Base):
    """
    Abstract base model providing:
      - id        (UUID, primary key, auto-generated)
      - created_at (timestamptz, set on insert)
      - updated_at (timestamptz, updated on every update)
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "id" not in kwargs:
            self.id = uuid.uuid4()
        if "created_at" not in kwargs:
            self.created_at = datetime.utcnow()
        if "updated_at" not in kwargs:
            self.updated_at = datetime.utcnow()
        if hasattr(self, "upvote_count") and getattr(self, "upvote_count") is None:
            self.upvote_count = 0


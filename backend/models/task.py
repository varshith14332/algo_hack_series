from sqlalchemy import String, Float, DateTime, Enum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base
from datetime import datetime, timezone
import enum


class TaskStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    verified = "verified"
    failed = "failed"
    cache_hit = "cache_hit"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_hash: Mapped[str] = mapped_column(String(64), index=True)
    task_type: Mapped[str] = mapped_column(String(50))
    prompt: Mapped[str] = mapped_column(Text)
    requester: Mapped[str] = mapped_column(String(58))
    tx_id: Mapped[str] = mapped_column(String(64), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.pending
    )
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    merkle_root: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ipfs_cid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_algo: Mapped[float] = mapped_column(Float, default=0.0)
    from_cache: Mapped[bool] = mapped_column(default=False)
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

from sqlalchemy import String, Float, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base
from datetime import datetime, timezone


class AgentActivity(Base):
    __tablename__ = "agent_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    agent_type: Mapped[str] = mapped_column(String(50))
    event: Mapped[str] = mapped_column(String(100))
    task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class AgentReputation(Base):
    __tablename__ = "agent_reputations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    agent_address: Mapped[str] = mapped_column(String(58), unique=True, index=True)
    agent_type: Mapped[str] = mapped_column(String(50))
    score: Mapped[float] = mapped_column(Float, default=500.0)
    total_tasks: Mapped[int] = mapped_column(Integer, default=0)
    successful_tasks: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

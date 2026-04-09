from sqlalchemy import String, Float, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base
from datetime import datetime, timezone


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tx_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    task_hash: Mapped[str] = mapped_column(String(64), index=True)
    sender: Mapped[str] = mapped_column(String(58))
    receiver: Mapped[str] = mapped_column(String(58))
    amount_algo: Mapped[float] = mapped_column(Float)
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

from sqlalchemy import String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from db.database import Base
from datetime import datetime, timezone


class Result(Base):
    __tablename__ = "results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    task_text: Mapped[str] = mapped_column(Text)
    result: Mapped[str] = mapped_column(Text)
    merkle_root: Mapped[str] = mapped_column(String(64))
    ipfs_cid: Mapped[str] = mapped_column(String(100))
    original_requester: Mapped[str] = mapped_column(String(58))
    price_microalgo: Mapped[int] = mapped_column(default=0)
    on_chain: Mapped[bool] = mapped_column(Boolean, default=False)
    chain_tx_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resale_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

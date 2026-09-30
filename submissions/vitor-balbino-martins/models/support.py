from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.base import Base, TimestampMixin


class SupportTicket(TimestampMixin, Base):
    __tablename__ = "support_tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    subject: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    channel: Mapped[str | None] = mapped_column(String(80), index=True)
    priority: Mapped[str | None] = mapped_column(String(40), index=True)
    ticket_type: Mapped[str | None] = mapped_column(String(120), index=True)
    source_status: Mapped[str | None] = mapped_column(String(80))
    kanban_stage: Mapped[str] = mapped_column(String(40), default="new", index=True, nullable=False)
    resolution_hours: Mapped[float | None] = mapped_column(Float)
    first_response_hours: Mapped[float | None] = mapped_column(Float)
    satisfaction: Mapped[float | None] = mapped_column(Float)
    source_dataset: Mapped[str] = mapped_column(String(255), nullable=False)
    source_row: Mapped[int] = mapped_column(Integer, nullable=False)


class DashboardSnapshot(TimestampMixin, Base):
    __tablename__ = "dashboard_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    dataset: Mapped[str] = mapped_column(String(255), index=True)
    ticket_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_resolution: Mapped[float | None] = mapped_column(Float)
    avg_first_response: Mapped[float | None] = mapped_column(Float)
    avg_satisfaction: Mapped[float | None] = mapped_column(Float)
    sla_rate: Mapped[float | None] = mapped_column(Float)
    estimated_cost: Mapped[float | None] = mapped_column(Float)
    recoverable_hours: Mapped[float | None] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


Index("ix_dashboard_dataset_generated", DashboardSnapshot.dataset, DashboardSnapshot.generated_at.desc())

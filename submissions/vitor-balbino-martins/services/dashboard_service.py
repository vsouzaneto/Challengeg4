import csv
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from models.support import DashboardSnapshot, SupportTicket


class DashboardService:
    @staticmethod
    def number(value):
        timestamp = re.search(r"\d{4}-\d{2}-\d{2}\s+(\d{1,2}):(\d{2})(?::(\d{2}))?", value or "")
        if timestamp: return float(timestamp.group(1)) + float(timestamp.group(2))/60 + float(timestamp.group(3) or 0)/3600
        match = re.search(r"\d+(?:\.\d+)?", value or "")
        return float(match.group()) if match else None

    @classmethod
    async def sync(cls, db: AsyncSession, dataset: str, hourly_cost: float | None = None):
        path = Path(__file__).resolve().parents[1] / settings.RAG_ASSETS_DIR / dataset
        with path.open("r", encoding="utf-8-sig", newline="") as file: rows = list(csv.DictReader(file))
        existing = {x.ticket_id: x for x in (await db.scalars(select(SupportTicket).where(SupportTicket.source_dataset == dataset))).all()}
        resolutions, responses, ratings = [], [], []
        for row_number, row in enumerate(rows, 2):
            rid = row.get("Ticket ID") or f"{dataset}:{row_number}"
            ticket = existing.get(rid) or SupportTicket(ticket_id=rid, source_dataset=dataset, source_row=row_number, kanban_stage="new")
            ticket.subject, ticket.description = row.get("Ticket Subject"), row.get("Ticket Description")
            ticket.channel, ticket.priority, ticket.ticket_type, ticket.source_status = row.get("Ticket Channel"), row.get("Ticket Priority"), row.get("Ticket Type"), row.get("Ticket Status")
            ticket.resolution_hours, ticket.first_response_hours, ticket.satisfaction = cls.number(row.get("Time to Resolution")), cls.number(row.get("First Response Time")), cls.number(row.get("Customer Satisfaction Rating"))
            resolutions += [ticket.resolution_hours] if ticket.resolution_hours is not None else []
            responses += [ticket.first_response_hours] if ticket.first_response_hours is not None else []
            ratings += [ticket.satisfaction] if ticket.satisfaction is not None else []
            db.add(ticket)
        avg_resolution = mean(resolutions) if resolutions else None
        benchmark = min(resolutions) if resolutions else 0
        recoverable = sum(max(0, x - benchmark) for x in resolutions)
        snapshot = DashboardSnapshot(dataset=dataset, ticket_count=len(rows), avg_resolution=avg_resolution, avg_first_response=mean(responses) if responses else None, avg_satisfaction=mean(ratings) if ratings else None, recoverable_hours=recoverable, estimated_cost=recoverable * hourly_cost if hourly_cost is not None else None, payload={"source": dataset, "synced_rows": len(rows)}, generated_at=datetime.now(timezone.utc))
        db.add(snapshot); await db.commit(); await db.refresh(snapshot)
        return snapshot

    @staticmethod
    def serialize(snapshot):
        return {"id": snapshot.id, "dataset": snapshot.dataset, "ticket_count": snapshot.ticket_count, "avg_resolution": snapshot.avg_resolution, "avg_first_response": snapshot.avg_first_response, "avg_satisfaction": snapshot.avg_satisfaction, "sla_rate": snapshot.sla_rate, "recoverable_hours": snapshot.recoverable_hours, "estimated_cost": snapshot.estimated_cost, "generated_at": snapshot.generated_at}

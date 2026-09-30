from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_db
from models.support import DashboardSnapshot, SupportTicket
from schemas.dashboard import StageUpdate, SyncRequest
from services.dashboard_service import DashboardService

router = APIRouter()

@router.get("")
async def dashboard(db: AsyncSession = Depends(get_db)):
    snapshot = await db.scalar(select(DashboardSnapshot).order_by(desc(DashboardSnapshot.generated_at)).limit(1))
    if not snapshot: raise HTTPException(404, "Nenhum snapshot persistido. Execute POST /dashboard/sync.")
    return DashboardService.serialize(snapshot)

@router.post("/sync", status_code=201)
async def sync_dashboard(request: SyncRequest, db: AsyncSession = Depends(get_db)):
    return DashboardService.serialize(await DashboardService.sync(db, request.dataset, request.hourly_cost))

@router.get("/tickets")
async def tickets(stage: str | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)):
    query = select(SupportTicket).order_by(SupportTicket.id).limit(min(limit, 500))
    if stage: query = query.where(SupportTicket.kanban_stage == stage)
    rows = (await db.scalars(query)).all()
    return [{"ticket_id": x.ticket_id, "subject": x.subject, "description": x.description, "channel": x.channel, "priority": x.priority, "ticket_type": x.ticket_type, "stage": x.kanban_stage, "satisfaction": x.satisfaction} for x in rows]

@router.patch("/tickets/{ticket_id}/stage")
async def move_ticket(ticket_id: str, update: StageUpdate, db: AsyncSession = Depends(get_db)):
    ticket = await db.scalar(select(SupportTicket).where(SupportTicket.ticket_id == ticket_id))
    if not ticket: raise HTTPException(404, "Ticket não encontrado")
    ticket.kanban_stage = update.stage; await db.commit()
    return {"ticket_id": ticket.ticket_id, "stage": ticket.kanban_stage}

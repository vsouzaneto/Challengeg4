"""persist support tickets and dashboard snapshots

Revision ID: 20260922_support_dashboard
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20260922_support_dashboard"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("support_tickets",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("ticket_id", sa.String(80), nullable=False),
        sa.Column("subject", sa.String(500)), sa.Column("description", sa.Text()), sa.Column("channel", sa.String(80)),
        sa.Column("priority", sa.String(40)), sa.Column("ticket_type", sa.String(120)), sa.Column("source_status", sa.String(80)),
        sa.Column("kanban_stage", sa.String(40), nullable=False, server_default="new"), sa.Column("resolution_hours", sa.Float()),
        sa.Column("first_response_hours", sa.Float()), sa.Column("satisfaction", sa.Float()), sa.Column("source_dataset", sa.String(255), nullable=False),
        sa.Column("source_row", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("ticket_id"))
    op.create_index("ix_support_tickets_stage", "support_tickets", ["kanban_stage"])
    op.create_index("ix_support_tickets_dataset", "support_tickets", ["source_dataset"])
    op.create_table("dashboard_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("dataset", sa.String(255), nullable=False),
        sa.Column("ticket_count", sa.Integer(), nullable=False), sa.Column("avg_resolution", sa.Float()),
        sa.Column("avg_first_response", sa.Float()), sa.Column("avg_satisfaction", sa.Float()), sa.Column("sla_rate", sa.Float()),
        sa.Column("estimated_cost", sa.Float()), sa.Column("recoverable_hours", sa.Float()), sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_dashboard_snapshots_dataset", "dashboard_snapshots", ["dataset"])


def downgrade():
    op.drop_table("dashboard_snapshots")
    op.drop_table("support_tickets")

"""Audit and points models"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from datetime import datetime
import uuid

from api.database import Base, UUID, IS_SQLITE

# JSON type (JSONB for PostgreSQL, JSON for SQLite)
if IS_SQLITE:
    JSONB = JSON
else:
    from api.database import JSONB


class AuditLog(Base):
    """Audit trail for all changes"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)  # item, ticket, parent, card
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)  # created, updated, approved, rejected
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    actor_type = Column(String(20), nullable=True)  # parent, admin, system
    changes = Column(JSONB, nullable=True)  # before/after values
    extra_metadata = Column(JSONB, nullable=True)  # parser_version, confidence scores, etc. (renamed from 'metadata')
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.id} {self.action} on {self.entity_type}>"


class PointTransaction(Base):
    """Gamification points ledger"""
    __tablename__ = "point_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)
    points = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # earned, redeemed, bonus, penalty
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PointTransaction {self.id} {self.points} {self.transaction_type}>"

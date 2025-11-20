"""Ticket model - crowdsourced corrections"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from api.database import Base, UUID, JSONB


class Ticket(Base):
    """Crowdsourced correction ticket"""
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    ticket_type = Column(String(50), nullable=False)  # error_report, suggestion, new_info
    description = Column(Text, nullable=False)
    proposed_changes = Column(JSONB, nullable=True)  # {field: {old: value, new: value}}
    status = Column(String(20), default="pending")  # pending, reviewing, approved, rejected
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    points_awarded = Column(Integer, default=0)
    qdrant_id = Column(Text, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Parent", back_populates="tickets")

    def __repr__(self):
        return f"<Ticket {self.id} {self.ticket_type} {self.status}>"

"""Card model - personalized digest cards"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from api.database import Base


class Card(Base):
    """Personalized digest card for a parent"""
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending")  # pending, done, dismissed
    delivered_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    reminder_sent_count = Column(Integer, default=0)
    last_reminder_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("Parent", back_populates="cards")
    item = relationship("Item", back_populates="cards")

    # Constraints
    __table_args__ = (
        UniqueConstraint('parent_id', 'item_id', name='uix_parent_item'),
    )

    def __repr__(self):
        return f"<Card {self.id} {self.status}>"

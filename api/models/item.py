"""Newsletter and item models"""
from sqlalchemy import Column, String, Text, Date, Time, Integer, DECIMAL, Boolean, DateTime, ForeignKey, BIGINT
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from api.database import Base


class Newsletter(Base):
    """Source newsletter document"""
    __tablename__ = "newsletters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    publish_date = Column(Date, nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(20), nullable=True)
    file_size_bytes = Column(BIGINT, nullable=True)
    parsed_at = Column(DateTime, nullable=True)
    parse_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    items_extracted = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("Item", back_populates="newsletter")

    def __repr__(self):
        return f"<Newsletter {self.id} {self.title}>"


class Item(Base):
    """Parsed newsletter item"""
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)  # Event, PermissionSlip, Fundraiser, HotLunch, Announcement
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=True)
    time = Column(Time, nullable=True)
    end_date = Column(Date, nullable=True)
    location = Column(String(255), nullable=True)
    audience_tags = Column(ARRAY(Text), nullable=False)  # e.g., ['grade_5', 'Basketball', 'all']
    action_link = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    cost = Column(DECIMAL(10, 2), nullable=True)

    # Source tracking
    source_newsletter_id = Column(UUID(as_uuid=True), ForeignKey("newsletters.id"), nullable=True)
    source_url = Column(Text, nullable=True)
    source_snippet = Column(Text, nullable=True)
    source_page = Column(Integer, nullable=True)

    # AI confidence
    confidence_score = Column(DECIMAL(3, 2), nullable=True)
    gemini_reasoning = Column(Text, nullable=True)

    # Status
    updated_flag = Column(Boolean, default=False)
    status = Column(String(20), default="pending")  # pending, approved, rejected, archived
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Qdrant integration
    qdrant_id = Column(Text, unique=True, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    newsletter = relationship("Newsletter", back_populates="items")
    cards = relationship("Card", back_populates="item")

    def __repr__(self):
        return f"<Item {self.id} {self.type}: {self.title}>"

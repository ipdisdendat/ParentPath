"""Parent and child models"""
from sqlalchemy import Column, String, Integer, Boolean, Time, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from api.database import Base
from api.database import UUID


class Parent(Base):
    """Parent/family account"""
    __tablename__ = "parents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_type = Column(String(20), nullable=False)  # whatsapp, sms, email
    channel_id = Column(String(255), nullable=False, unique=True)
    language = Column(String(5), default="en")  # ISO 639-1
    timezone = Column(String(50), default="America/Vancouver")
    quiet_hours_start = Column(Time, default=datetime.strptime("22:00", "%H:%M").time())
    quiet_hours_end = Column(Time, default=datetime.strptime("08:00", "%H:%M").time())
    heads_up_mode = Column(Boolean, default=False)
    trust_score = Column(DECIMAL(3, 2), default=0.5)
    points_balance = Column(Integer, default=0)
    onboarded_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="active")  # active, paused, unsubscribed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="parent", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="parent")
    messages = relationship("MessageLog", back_populates="parent")
    tickets = relationship("Ticket", back_populates="parent")

    def __repr__(self):
        return f"<Parent {self.id} {self.channel_type}:{self.channel_id}>"


class Child(Base):
    """Child in household"""
    __tablename__ = "children"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=True)
    grade = Column(Integer, nullable=False)
    division = Column(String(10), nullable=True)
    school_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Parent", back_populates="children")
    subscriptions = relationship("Subscription", back_populates="child", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Child {self.id} Grade {self.grade}>"


class Subscription(Base):
    """Activity subscriptions"""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    activity = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("Parent", back_populates="subscriptions")
    child = relationship("Child", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription {self.id} {self.activity}>"

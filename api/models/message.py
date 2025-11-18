"""Message log model"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from api.database import Base


class MessageLog(Base):
    """Message delivery log"""
    __tablename__ = "message_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id"), nullable=False)
    card_id = Column(UUID(as_uuid=True), ForeignKey("cards.id"), nullable=True)
    message_type = Column(String(50), nullable=False)  # digest, reminder, delta, reply, onboarding
    channel = Column(String(20), nullable=False)  # whatsapp, sms, email
    message_sid = Column(String(100), nullable=True)  # Twilio/WhatsApp message ID
    status = Column(String(20), default="sent")  # sent, delivered, read, failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    parent = relationship("Parent", back_populates="messages")

    def __repr__(self):
        return f"<MessageLog {self.id} {self.message_type} {self.status}>"

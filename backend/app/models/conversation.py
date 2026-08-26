from sqlalchemy import Column, String, DateTime, func, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String, nullable=False) # 'whatsapp' or 'telegram'
    customer_identifier = Column(String, nullable=False) # Phone number or User ID
    customer_name = Column(String, nullable=True) # Null for WhatsApp usually
    status = Column(String, nullable=False, default="ai_handling") # ai_handling, manual, needs_human
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_unread = Column(Boolean, nullable=False, default=False)
    satisfaction = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    business = relationship("Business", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

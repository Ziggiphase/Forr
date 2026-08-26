from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    amount = Column(Integer, nullable=False) # in smallest currency unit (e.g. kobo/cents)
    currency = Column(String, nullable=False, default="NGN")
    
    status = Column(String, nullable=False, default="pending") # pending, success, failed
    paystack_reference = Column(String, nullable=False, unique=True, index=True)
    customer_identifier = Column(String, nullable=True, index=True)
    
    # Can add other fields like product_id later if needed

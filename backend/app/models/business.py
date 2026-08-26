from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    integration_types = Column(JSONB, nullable=False, default=list)
    address = Column(String, nullable=False)
    size = Column(String, nullable=False)
    service_mode = Column(String, nullable=False)
    encrypted_telegram_token = Column(String, nullable=True)
    encrypted_twilio_sid = Column(String, nullable=True)
    encrypted_twilio_auth_token = Column(String, nullable=True)
    twilio_phone_number = Column(String, nullable=True)

    paystack_subaccount_code = Column(String, nullable=True)
    bank_account_number = Column(String, nullable=True)
    bank_code = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    bank_account_name = Column(String, nullable=True)

    agent_knowledge = Column(JSONB, nullable=False, default=dict)
    agent_tone = Column(String, nullable=True)
    total_tokens_used = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    owner = relationship("User", back_populates="businesses")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="business", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="business", uselist=False, cascade="all, delete-orphan")

    @property
    def conversation_limit(self) -> int:
        tier = self.subscription.plan_tier if self.subscription else "free"
        if tier == "pro":
            return 500
        elif tier == "premium":
            return 5000
        return 50 # default free tier limit

    @property
    def is_telegram_connected(self) -> bool:
        return self.encrypted_telegram_token is not None

    @property
    def is_whatsapp_connected(self) -> bool:
        return self.encrypted_twilio_sid is not None and self.encrypted_twilio_auth_token is not None

from sqlalchemy import Column, String, Date, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nin = Column(String, nullable=True) # Stored unverified for now
    dob = Column(Date, nullable=False)
    nationality = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    state = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=False, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    businesses = relationship("Business", back_populates="owner", cascade="all, delete-orphan", lazy="selectin")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    @property
    def total_tokens_used(self) -> int:
        return sum(b.total_tokens_used for b in self.businesses)

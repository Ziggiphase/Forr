from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ConversationStatusUpdate(BaseModel):
    status: str

class MessageCreate(BaseModel):
    content: str

class MessageRead(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_type: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationRead(BaseModel):
    id: UUID
    business_id: UUID
    channel: str
    customer_identifier: str
    customer_name: str | None
    status: str
    last_activity_at: datetime
    is_unread: bool
    created_at: datetime
    updated_at: datetime
    
    # We can also include the last message snippet if needed, but for now we'll just return the base model
    
    class Config:
        from_attributes = True

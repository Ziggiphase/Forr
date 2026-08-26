from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class BusinessBase(BaseModel):
    name: str
    business_type: str
    description: Optional[str] = None
    integration_types: List[str] = Field(default_factory=list)
    address: str
    size: str
    service_mode: str

class BusinessCreate(BusinessBase):
    pass

class BusinessRead(BusinessBase):
    id: UUID
    owner_id: UUID
    is_telegram_connected: bool = False
    is_whatsapp_connected: bool = False
    agent_knowledge: dict = Field(default_factory=dict)
    agent_tone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BusinessAgentConfigUpdate(BaseModel):
    agent_knowledge: dict
    agent_tone: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

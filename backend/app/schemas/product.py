from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    quantity: int = Field(default=0)
    category: str
    status: str = Field(default="draft")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    status: Optional[str] = None

class ProductRead(ProductBase):
    id: UUID
    business_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

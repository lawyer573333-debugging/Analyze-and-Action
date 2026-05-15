from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    content_type: str
    source_type: str
    source_url: Optional[str] = None

class DocumentCreate(DocumentBase):
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    storage_path: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: str
    user_id: str
    uploaded_at: datetime
    file_size: Optional[int] = None

    class Config:
        from_attributes = True

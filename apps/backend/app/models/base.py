from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

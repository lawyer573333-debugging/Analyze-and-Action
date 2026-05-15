from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from app.models.base import Base, generate_uuid, utc_now
import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free")
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

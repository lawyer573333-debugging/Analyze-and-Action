from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.models.base import Base, generate_uuid, utc_now
import datetime

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False) # pdf, url, text
    source_url: Mapped[Optional[str]] = mapped_column(String(1024))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    file_hash: Mapped[Optional[str]] = mapped_column(String(255))
    storage_path: Mapped[Optional[str]] = mapped_column(String(1024))
    
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    owner = relationship("User", back_populates="documents")

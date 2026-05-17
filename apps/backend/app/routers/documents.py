from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, List

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse
from app.routers.auth import get_current_user
from app.config import settings
import uuid
import datetime

router = APIRouter()

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(None),
    source_url: str = Form(None),
    source_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Configuration
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_CONTENT_TYPES = {"application/pdf", "text/plain", "text/html"}
    
    if source_type not in ["pdf", "url", "text"]:
        raise HTTPException(status_code=400, detail="Invalid source type. Must be pdf, url, or text")
    
    if source_type == "pdf" and not file:
        raise HTTPException(status_code=400, detail="PDF file is required for source_type pdf")
        
    if source_type == "url" and not source_url:
        raise HTTPException(status_code=400, detail="URL is required for source_type url")

    file_size = 0
    if file:
        # Read file contents and validate
        file_contents = await file.read()
        file_size = len(file_contents)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )
        
        # Validate content type
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
            )
    
    filename = file.filename if file else f"url_source_{uuid.uuid4().hex[:8]}"
    content_type = file.content_type if file else "text/plain"
    
    doc = Document(
        user_id=current_user.id,
        filename=filename,
        content_type=content_type,
        source_type=source_type,
        source_url=source_url,
        file_size=file_size
    )
    
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    return doc

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Get active documents for the current user
    stmt = select(Document).where(
        Document.user_id == current_user.id,
        Document.deleted_at.is_(None)
    ).order_by(Document.uploaded_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return documents

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Document).where(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Soft delete
    from app.models.base import utc_now
    document.deleted_at = utc_now()
    await db.commit()
    
    return {"status": "deleted"}

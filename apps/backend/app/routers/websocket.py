from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/{document_id}")
async def websocket_endpoint(websocket: WebSocket, document_id: str):
    await manager.connect(websocket, document_id)
    try:
        while True:
            # We don't expect the client to send much data, but we need to keep the connection open
            # and listen for possible client disconnects.
            data = await websocket.receive_text()
            logger.info(f"Received message from client for document {document_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, document_id)

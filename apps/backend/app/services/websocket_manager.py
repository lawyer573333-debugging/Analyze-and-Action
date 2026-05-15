from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps document_id to a list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, document_id: str):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
        self.active_connections[document_id].append(websocket)
        logger.info(f"WebSocket connected for document {document_id}")

    def disconnect(self, websocket: WebSocket, document_id: str):
        if document_id in self.active_connections:
            if websocket in self.active_connections[document_id]:
                self.active_connections[document_id].remove(websocket)
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]
        logger.info(f"WebSocket disconnected for document {document_id}")

    async def broadcast(self, message: dict, document_id: str):
        if document_id in self.active_connections:
            for connection in self.active_connections[document_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to websocket: {e}")

manager = ConnectionManager()

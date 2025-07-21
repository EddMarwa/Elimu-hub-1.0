import json
from typing import Dict, Set
from fastapi import WebSocket
from app.utils.logger import logger

class UploadProgressManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected to upload progress")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected from upload progress")
    
    async def send_progress(self, user_id: int, job_id: str, progress: Dict):
        if user_id in self.active_connections:
            message = {
                "type": "upload_progress",
                "job_id": job_id,
                "progress": progress
            }
            for connection in self.active_connections[user_id].copy():
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending progress to user {user_id}: {e}")
                    self.disconnect(connection, user_id)

upload_manager = UploadProgressManager()

async def send_upload_progress(user_id: int, job_id: str, progress: Dict):
    """Send upload progress to connected clients."""
    await upload_manager.send_progress(user_id, job_id, progress) 
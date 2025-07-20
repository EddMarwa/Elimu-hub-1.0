from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.auth.dependencies import get_current_user_ws
from app.auth.models import User
from app.services.job_queue import job_queue
from app.utils.logger import logger
import json
from typing import Dict, Set

router = APIRouter()

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

@router.websocket("/ws/upload-progress")
async def upload_progress_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time upload progress tracking."""
    user = None
    try:
        # Authenticate user
        user = await get_current_user_ws(websocket)
        if not user:
            await websocket.close(code=4001, reason="Authentication required")
            return
        
        await upload_manager.connect(websocket, user.id)
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Connected to upload progress tracking"
        }))
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "subscribe_job":
                    job_id = message.get("job_id")
                    if job_id:
                        # Subscribe to specific job updates
                        await websocket.send_text(json.dumps({
                            "type": "subscribed",
                            "job_id": job_id
                        }))
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in upload progress websocket: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in upload progress websocket: {e}")
    finally:
        if user:
            upload_manager.disconnect(websocket, user.id)

# Function to be called by job queue to send progress updates
async def send_upload_progress(user_id: int, job_id: str, progress: Dict):
    """Send upload progress to connected clients."""
    await upload_manager.send_progress(user_id, job_id, progress) 
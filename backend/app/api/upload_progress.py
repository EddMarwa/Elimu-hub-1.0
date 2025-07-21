from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.auth.dependencies import get_current_user_ws
from app.auth.models import User
from app.services.upload_utils import upload_manager, send_upload_progress
from app.utils.logger import logger
import json
from typing import Dict, Set

router = APIRouter()

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
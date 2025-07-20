from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from app.auth.dependencies import get_current_admin_user
from app.auth.models import User
from app.db.database import SessionLocal
from app.models.document import Document
from app.models.chat import ChatSession, ChatMessage
from app.utils.logger import logger
import json
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.get("/export/documents")
async def export_documents(
    format: str = "json",
    current_user: User = Depends(get_current_admin_user)
):
    """Export all documents in JSON or CSV format (admin only)."""
    try:
        db = SessionLocal()
        documents = db.query(Document).all()
        
        if format.lower() == "csv":
            # Create CSV export
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Title", "File Type", "File Size", 
                "Uploaded At", "Content Length", "User ID"
            ])
            
            # Write data
            for doc in documents:
                writer.writerow([
                    doc.id, doc.title, doc.file_type, doc.file_size,
                    doc.uploaded_at.isoformat(), len(doc.content), doc.user_id
                ])
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        
        else:  # JSON format
            documents_data = []
            for doc in documents:
                documents_data.append({
                    "id": doc.id,
                    "title": doc.title,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "content": doc.content,
                    "user_id": doc.user_id
                })
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_documents": len(documents_data),
                "documents": documents_data
            }
            
            return StreamingResponse(
                io.BytesIO(json.dumps(export_data, indent=2).encode()),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
            )
    
    except Exception as e:
        logger.error(f"Error exporting documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed"
        )
    finally:
        db.close()

@router.get("/export/chat-history")
async def export_chat_history(
    session_id: Optional[int] = None,
    format: str = "json",
    current_user: User = Depends(get_current_admin_user)
):
    """Export chat history in JSON or CSV format (admin only)."""
    try:
        db = SessionLocal()
        
        if session_id:
            sessions = db.query(ChatSession).filter(ChatSession.id == session_id).all()
        else:
            sessions = db.query(ChatSession).all()
        
        if format.lower() == "csv":
            # Create CSV export
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Session ID", "User ID", "Title", "Created At", 
                "Message ID", "Role", "Content", "Timestamp"
            ])
            
            # Write data
            for session in sessions:
                for message in session.messages:
                    writer.writerow([
                        session.id, session.user_id, session.title,
                        session.created_at.isoformat(), message.id,
                        message.role, message.content, message.timestamp.isoformat()
                    ])
            
            output.seek(0)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        
        else:  # JSON format
            sessions_data = []
            for session in sessions:
                session_data = {
                    "id": session.id,
                    "user_id": session.user_id,
                    "title": session.title,
                    "created_at": session.created_at.isoformat(),
                    "messages": []
                }
                
                for message in session.messages:
                    session_data["messages"].append({
                        "id": message.id,
                        "role": message.role,
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat()
                    })
                
                sessions_data.append(session_data)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_sessions": len(sessions_data),
                "sessions": sessions_data
            }
            
            return StreamingResponse(
                io.BytesIO(json.dumps(export_data, indent=2).encode()),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
            )
    
    except Exception as e:
        logger.error(f"Error exporting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed"
        )
    finally:
        db.close()

@router.post("/import/documents")
async def import_documents(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Import documents from JSON file (admin only)."""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JSON files are supported for import"
            )
        
        content = await file.read()
        import_data = json.loads(content.decode())
        
        if "documents" not in import_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid import file format"
            )
        
        db = SessionLocal()
        imported_count = 0
        
        for doc_data in import_data["documents"]:
            try:
                # Check if document already exists
                existing = db.query(Document).filter(Document.title == doc_data["title"]).first()
                if existing:
                    logger.warning(f"Document {doc_data['title']} already exists, skipping")
                    continue
                
                # Create new document
                document = Document(
                    title=doc_data["title"],
                    file_type=doc_data["file_type"],
                    file_size=doc_data["file_size"],
                    content=doc_data["content"],
                    user_id=doc_data.get("user_id", current_user.id)
                )
                
                db.add(document)
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Error importing document {doc_data.get('title', 'unknown')}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"Admin user {current_user.email} imported {imported_count} documents")
        
        return {
            "message": f"Successfully imported {imported_count} documents",
            "total_in_file": len(import_data["documents"]),
            "imported_count": imported_count
        }
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON file"
        )
    except Exception as e:
        logger.error(f"Error importing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Import failed"
        )
    finally:
        db.close()

@router.get("/export/system-stats")
async def export_system_stats(
    current_user: User = Depends(get_current_admin_user)
):
    """Export system statistics (admin only)."""
    try:
        db = SessionLocal()
        
        # Get basic stats
        total_documents = db.query(Document).count()
        total_users = db.query(User).count()
        total_sessions = db.query(ChatSession).count()
        total_messages = db.query(ChatMessage).count()
        
        # Get file type distribution
        file_types = db.query(
            Document.file_type,
            db.func.count(Document.id).label('count')
        ).group_by(Document.file_type).all()
        
        # Get user activity
        user_activity = db.query(
            User.email,
            db.func.count(Document.id).label('documents'),
            db.func.count(ChatSession.id).label('sessions')
        ).outerjoin(Document).outerjoin(ChatSession).group_by(User.id, User.email).all()
        
        stats = {
            "export_date": datetime.now().isoformat(),
            "summary": {
                "total_documents": total_documents,
                "total_users": total_users,
                "total_sessions": total_sessions,
                "total_messages": total_messages
            },
            "file_types": [{"type": ft.file_type, "count": ft.count} for ft in file_types],
            "user_activity": [
                {
                    "email": ua.email,
                    "documents": ua.documents,
                    "sessions": ua.sessions
                }
                for ua in user_activity
            ]
        }
        
        return StreamingResponse(
            io.BytesIO(json.dumps(stats, indent=2).encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=system_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
        )
    
    except Exception as e:
        logger.error(f"Error exporting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed"
        )
    finally:
        db.close() 
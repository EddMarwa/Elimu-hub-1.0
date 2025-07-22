from fastapi import APIRouter, HTTPException, status, Query
from app.db.database import SessionLocal
from app.db.database import Document
from app.services.vector_store import vector_store
from app.services.cache import cache_service
from app.utils.logger import logger
from sqlalchemy import desc, asc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

router = APIRouter()

@router.get("/search/advanced", response_model=Dict[str, Any])
async def advanced_search(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("relevance", description="Sort by: relevance, date, title, size"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    file_type: Optional[str] = Query(None, description="Filter by file type (pdf, txt, etc.)"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    min_size: Optional[int] = Query(None, ge=0, description="Minimum file size in bytes"),
    max_size: Optional[int] = Query(None, ge=0, description="Maximum file size in bytes"),
    include_content: bool = Query(False, description="Include document content in results")
):
    """Advanced search with filtering, sorting, and pagination."""
    try:
        db = SessionLocal()
        base_query = db.query(Document)
        
        # Apply filters
        if file_type:
            base_query = base_query.filter(Document.file_type == file_type.lower())
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                base_query = base_query.filter(Document.uploaded_at >= from_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use YYYY-MM-DD"
                )
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                base_query = base_query.filter(Document.uploaded_at <= to_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use YYYY-MM-DD"
                )
        
        if min_size is not None:
            base_query = base_query.filter(Document.file_size >= min_size)
        
        if max_size is not None:
            base_query = base_query.filter(Document.file_size <= max_size)
        
        # Apply sorting
        if sort_by == "date":
            order_func = desc if sort_order == "desc" else asc
            base_query = base_query.order_by(order_func(Document.uploaded_at))
        elif sort_by == "title":
            order_func = desc if sort_order == "desc" else asc
            base_query = base_query.order_by(order_func(Document.title))
        elif sort_by == "size":
            order_func = desc if sort_order == "desc" else asc
            base_query = base_query.order_by(order_func(Document.file_size))
        # relevance sorting will be applied after vector search
        
        # Get filtered documents
        filtered_docs = base_query.all()
        
        if not filtered_docs:
            return {
                "results": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "filters_applied": {
                    "file_type": file_type,
                    "date_from": date_from,
                    "date_to": date_to,
                    "min_size": min_size,
                    "max_size": max_size
                }
            }
        
        # Perform vector search on filtered documents
        doc_ids = [doc.id for doc in filtered_docs]
        search_results = vector_store.search(query, doc_ids=doc_ids, limit=len(filtered_docs))
        
        # Combine vector search results with database info
        results = []
        for result in search_results:
            doc = next((d for d in filtered_docs if d.id == result["id"]), None)
            if doc:
                doc_data = {
                    "id": doc.id,
                    "title": doc.title,
                    "file_type": doc.file_type,
                    "file_size": doc.file_size,
                    "uploaded_at": doc.uploaded_at.isoformat(),
                    "similarity_score": result["score"],
                    "chunk_content": result["content"]
                }
                
                if include_content:
                    doc_data["content"] = doc.content
                
                results.append(doc_data)
        
        # Apply relevance sorting if requested
        if sort_by == "relevance":
            results.sort(key=lambda x: x["similarity_score"], reverse=(sort_order == "desc"))
        
        # Apply pagination
        total = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]
        
        # Log search activity
        logger.info(f"Advanced search performed: {query}")
        
        return {
            "results": paginated_results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "filters_applied": {
                "file_type": file_type,
                "date_from": date_from,
                "date_to": date_to,
                "min_size": min_size,
                "max_size": max_size
            }
        }
        
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )
    finally:
        db.close()

@router.get("/search/facets", response_model=Dict[str, Any])
async def get_search_facets():
    """Get search facets for filtering (file types, date ranges, etc.)."""
    try:
        db = SessionLocal()
        
        # Get file type distribution
        file_types = db.query(
            Document.file_type,
            db.func.count(Document.id).label('count')
        ).group_by(Document.file_type).all()
        
        # Get date range
        date_range = db.query(
            db.func.min(Document.uploaded_at).label('min_date'),
            db.func.max(Document.uploaded_at).label('max_date')
        ).first()
        
        # Get size range
        size_range = db.query(
            db.func.min(Document.file_size).label('min_size'),
            db.func.max(Document.file_size).label('max_size')
        ).first()
        
        return {
            "file_types": [{"type": ft.file_type, "count": ft.count} for ft in file_types],
            "date_range": {
                "min": date_range.min_date.isoformat() if date_range.min_date else None,
                "max": date_range.max_date.isoformat() if date_range.max_date else None
            },
            "size_range": {
                "min": size_range.min_size,
                "max": size_range.max_size
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting search facets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search facets"
        )
    finally:
        db.close() 
from fastapi import APIRouter, Query, HTTPException, status
from app.db.fts import search_documents
from app.utils.logger import logger
from typing import List

router = APIRouter()

@router.get("/search-documents")
async def search_documents_api(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """Search documents by content and metadata."""
    try:
        results = search_documents(q, limit)
        logger.info(f"Searched documents: '{q}' ({len(results)} results)")
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents"
        ) 
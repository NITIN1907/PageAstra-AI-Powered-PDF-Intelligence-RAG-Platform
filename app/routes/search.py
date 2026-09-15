from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.service.search_service import search_service


router = APIRouter()


class SearchRequest(BaseModel):

    query: str
    top_k: int = 5


@router.post("/search")
def search(
    request: SearchRequest
):

    try:

        results = search_service.search(
            request.query,
            request.top_k
        )

        return {
            "results": results
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
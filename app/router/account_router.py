from fastapi import APIRouter

from app.core.model import HttpResponse, success_response
from app.core.exception import CustomHTTPException


router = APIRouter()


@router.post("/account/test", response_model=HttpResponse)
async def test():
    card = None
    return success_response(data=card)

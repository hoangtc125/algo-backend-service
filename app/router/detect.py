from enum import Enum
from fastapi import APIRouter, Query

from app.core.model import HttpResponse, success_response
from app.core.api import DetectAPI
from app.core.exception import CustomHTTPException


class School(str, Enum):
    HUST = "HUST"
    HUCE = "HUCE"
    NEU = "NEU"


router = APIRouter()


@router.get("/detect/test-file", response_model=HttpResponse)
async def test_file(send_mail: bool, school: School = Query(...)):
    card = None
    if send_mail:
        pass
    return success_response(data=card)


@router.get("/detect/test-cam", response_model=HttpResponse)
async def test_cam(send_mail: bool, school: School = Query(...)):
    card = None
    if send_mail:
        pass
    return success_response(data=card)

from enum import Enum
import requests
from fastapi import APIRouter, Query, BackgroundTasks

from app.core.model import HttpResponse, success_response
from app.core.api import DetectAPI
from app.core.exception import CustomHTTPException
from app.service.mail import make_and_send_mail_card


class School(str, Enum):
    HUST = "HUST"
    HUCE = "HUCE"
    NEU = "NEU"


router = APIRouter()


@router.get("/detect/test-file", response_model=HttpResponse)
async def test_file(
    background_tasks: BackgroundTasks, send_mail: bool, school: School = Query(...)
):
    card = None
    if send_mail:
        background_tasks.add_task(make_and_send_mail_card, card.__dict__)
    return success_response(data=card)


@router.get("/detect/test-cam", response_model=HttpResponse)
async def test_cam(
    background_tasks: BackgroundTasks, send_mail: bool, school: School = Query(...)
):
    card = None
    if send_mail:
        background_tasks.add_task(make_and_send_mail_card, card.__dict__)
    return success_response(data=card)

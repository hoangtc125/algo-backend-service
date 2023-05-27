import requests
import concurrent.futures
from enum import Enum
from fastapi import APIRouter, Query

from app.core.config import project_config
from app.core.model import HttpResponse, success_response
from app.core.exception import CustomHTTPException
from app.service.detect import (
    detect_text_from_base64,
    detect_code_from_base64,
    file_to_base64,
    byte_to_base64,
    make_card_huce,
    make_card_hust,
    make_card_hust2,
    make_card_neu,
    make_card_neu2,
)
from app.worker.mail import mail_worker
from app.util.mail import Email, make_mail_verify_account


class School(str, Enum):
    HUST = "HUST"
    HUST2 = "HUST2"
    HUCE = "HUCE"
    NEU = "NEU"
    NEU2 = "NEU2"


router = APIRouter()


@router.get("/detect/test-file", response_model=HttpResponse)
async def test_file(send_mail: bool, school: School = Query(...)):
    if school == School.HUST.value:
        file_path = r"/home/hoangtc125/Downloads/20194060-Trần Công Hoàng.jpg"
        image_base64 = file_to_base64(file_path)
        info_list = detect_text_from_base64(image_base64)
        code_list = detect_code_from_base64(image_base64)
        card = make_card_hust(info_list)
        if card.number not in code_list:
            raise CustomHTTPException(error_type="detect_barcode_failure")
    elif school == School.HUCE.value:
        file_path = r"/home/hoangtc125/Downloads/6447cd41859a5ac4038b.jpg"
        image_base64 = file_to_base64(file_path)
        info_list = detect_text_from_base64(image_base64)
        card = make_card_huce(info_list)
    elif school == School.NEU.value:
        file_path = r"/home/hoangtc125/Downloads/neu.jpg"
        image_base64 = file_to_base64(file_path)
        info_list = detect_text_from_base64(image_base64)
        card = make_card_neu(info_list)
    if send_mail:
        mail_worker.push(
            Email(
                receiver_email=card.email,
                subject="Yêu cầu xác thực tài khoản",
                content=make_mail_verify_account(
                    card.__dict__,
                    f"http://{project_config.HOST}:{project_config.ALGO_PORT}/account/verify?token={1}",
                ),
            )
        )
    return success_response(data=card)


@router.get("/detect/test-file-future", response_model=HttpResponse)
async def test_file_future(send_mail: bool, school: School = Query(...)):
    if school == School.HUST.value:
        file_path = r"/media/hoangtc125/Windows/Users/ADMIN/Pictures/20194060-Trần Công Hoàng.jpg"
        image_base64 = file_to_base64(file_path)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_text = executor.submit(detect_text_from_base64, image_base64)
            future_barcode = executor.submit(detect_code_from_base64, image_base64)
            info_list = future_text.result()
            code_list = future_barcode.result()
        card = make_card_hust(info_list)
        if card.number not in code_list:
            raise CustomHTTPException(error_type="detect_barcode_failure")
    elif school == School.HUCE.value:
        file_path = r"/home/hoangtc125/Downloads/6447cd41859a5ac4038b.jpg"
        image_base64 = file_to_base64(file_path)
        info_list = detect_text_from_base64(image_base64)
        card = make_card_huce(info_list)
    elif school == School.NEU.value:
        file_path = r"/home/hoangtc125/Downloads/neu.jpg"
        image_base64 = file_to_base64(file_path)
        info_list = detect_text_from_base64(image_base64)
        card = make_card_neu(info_list)
    if send_mail:
        pass
    return success_response(data=card)


@router.get("/detect/test-cam", response_model=HttpResponse)
async def test_cam(send_mail: bool, school: School = Query(...)):
    url = "http://192.168.1.222:8080/photo.jpg"
    try:
        response = requests.get(url, timeout=2)
    except:
        raise CustomHTTPException(error_type="cam_timeout")
    img_data = response.content
    image_base64 = byte_to_base64(img_data)
    info_list = detect_text_from_base64(image_base64)
    if school == School.HUST.value:
        card = make_card_hust(info_list)
    if school == School.HUST2.value:
        card = make_card_hust2(info_list)
    elif school == School.HUCE.value:
        card = make_card_huce(info_list)
    elif school == School.NEU.value:
        card = make_card_neu(info_list)
    elif school == School.NEU2.value:
        card = make_card_neu2(info_list)
    if send_mail:
        pass
    return success_response(data=card)


@router.get("/detect/test-cam-future", response_model=HttpResponse)
async def test_cam_future(send_mail: bool, school: School = Query(...)):
    url = "http://192.168.1.222:8080/photo.jpg"
    try:
        response = requests.get(url, timeout=2)
    except:
        raise CustomHTTPException(error_type="cam_timeout")
    img_data = response.content
    image_base64 = byte_to_base64(img_data)
    if school == School.HUST.value:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_text = executor.submit(detect_text_from_base64, image_base64)
            future_barcode = executor.submit(detect_code_from_base64, image_base64)
            info_list = future_text.result()
            code_list = future_barcode.result()
        card = make_card_hust(info_list)
        if card.number not in code_list:
            raise CustomHTTPException(error_type="detect_barcode_failure")
    elif school == School.HUCE.value:
        card = make_card_huce(info_list)
    elif school == School.NEU.value:
        card = make_card_neu(info_list)
    if send_mail:
        pass
    return success_response(data=card)


@router.get("/detect/test-barcode", response_model=HttpResponse)
async def test_barcode(school: School = Query(...)):
    if school == School.HUST.value:
        file_path = r"/media/hoangtc125/Windows/Users/ADMIN/Pictures/20194060-Trần Công Hoàng.jpg"
    elif school == School.HUCE.value:
        file_path = r"/home/hoangtc125/Downloads/6447cd41859a5ac4038b.jpg"
    elif school == School.NEU.value:
        file_path = r"/home/hoangtc125/Downloads/neu.jpg"
    decode_data_list = detect_code_from_base64(file_to_base64(file_path))
    return success_response(data=decode_data_list)


@router.get("/detect/test-future", response_model=HttpResponse)
async def test_future(future: bool):
    url = "http://192.168.1.222:8080/photo.jpg"
    try:
        response = requests.get(url, timeout=2)
    except:
        raise CustomHTTPException(error_type="cam_timeout")
    img_data = response.content
    image_base64 = byte_to_base64(img_data)
    if future:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_text = executor.submit(detect_text_from_base64, image_base64)
            future_barcode = executor.submit(detect_code_from_base64, image_base64)
            info_list = future_text.result()
            code_list = future_barcode.result()
    else:
        info_list = detect_text_from_base64(image_base64)
        code_list = detect_code_from_base64(image_base64)
    return success_response(data={"info_list": info_list, "code_list": code_list})

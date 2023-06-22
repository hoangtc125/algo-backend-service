import os
import base64
import difflib
import re
import numpy as np
from google.cloud import vision
from typing import Dict, List

# from pyzbar.pyzbar import decode

from app.core.config import project_config
from app.core.exception import CustomHTTPException
from app.model.card import CardHUCE, CardHUST, CardHUST2, CardNEU, CardNEU2

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = project_config.VISION_CONFIG_PATH


def file_to_base64(path: str):
    with open(path, "rb") as image_file:
        image_data = image_file.read()
    encoded_image = byte_to_base64(image_data)
    return encoded_image


def byte_to_base64(data):
    return base64.b64encode(data).decode("utf-8")


def detect_info(detect_guide: Dict, info_list: List):
    return {attr: search(info_list, guide) for attr, guide in detect_guide.items()}


def search(info_list: List, value: str):
    match_list = difflib.get_close_matches(value, info_list)
    if not match_list:
        raise CustomHTTPException(
            error_type="detect_invalid", message=f"{value} not found"
        )
    return info_list.index(match_list[0])


def detect_text_from_base64(image_base64: str):
    vision_client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.content = base64.b64decode(image_base64)
    response = vision_client.text_detection(image=image, timeout=10)
    try:
        info_text = response.text_annotations[0].description
        info_list = info_text.split("\n")
        return info_list
    except:
        raise CustomHTTPException(error_type="detect_info_failure")


def detect_code_from_base64(image_base64: str):
    #     decoded_data = base64.b64decode(image_base64)
    #     np_data = np.frombuffer(decoded_data, dtype=np.uint8)
    #     img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
    #     img = cv2.GaussianBlur(img, (5, 5), 0)  # Làm mờ ảnh để loại bỏ noise
    #     gray_img = cv2.cvtColor(
    #         img, cv2.COLOR_BGR2GRAY
    #     )  # Chuyển sang ảnh xám để dễ dàng nhận diện
    #     alpha = 1.5  # giá trị alpha tăng độ sáng
    #     beta = 0  # giá trị beta tăng độ sáng
    #     bright_img = cv2.convertScaleAbs(gray_img, alpha=alpha, beta=beta)
    #     barcodes = decode(bright_img)  # Nhận diện mã vạch
    #     barcode_list = [barcode.data.decode() for barcode in barcodes]
    #     return barcode_list
    return None


def make_card_hust(info_list):
    ids_detect = detect_info(CardHUST.get_detect_guide(), info_list)
    return CardHUST(
        school=info_list[ids_detect["school"]],
        fullname=info_list[ids_detect["fullname"] + 1],
        major=info_list[ids_detect["birth"] + 2],
        birth=info_list[ids_detect["birth"] + 1],
        expired_card=info_list[ids_detect["expired_card"] + 1],
        number=info_list[ids_detect["number"] + 1],
    )


def make_card_hust2(info_list):
    ids_detect = detect_info(CardHUST2.get_detect_guide(), info_list)
    return CardHUST2(
        school=info_list[ids_detect["school"]],
        fullname=info_list[ids_detect["fullname"] + 1],
        major=info_list[ids_detect["expired_card"] - 1],
        birth=info_list[ids_detect["birth"] + 1],
        expired_card=info_list[ids_detect["expired_card"] + 1],
        number=info_list[ids_detect["number"] + 1],
    )


def make_card_huce(info_list):
    ids_detect = detect_info(CardHUCE.get_detect_guide(), info_list)
    return CardHUCE(
        school=info_list[ids_detect["school"]],
        major=info_list[ids_detect["major"]],
        fullname=info_list[ids_detect["number"] - 2],
        birth=info_list[ids_detect["number"] - 1],
        expired_card=info_list[ids_detect["expired_card"]],
        number=info_list[ids_detect["number"]],
        email=info_list[ids_detect["email"]],
    )


def make_card_neu(info_list):
    ids_detect = detect_info(CardNEU.get_detect_guide(), info_list)
    return CardNEU(
        school=info_list[ids_detect["school"]],
        major=info_list[ids_detect["fullname"] + 3],
        fullname=info_list[ids_detect["fullname"] + 1],
        birth=info_list[ids_detect["fullname"] + 2],
        expired_card=info_list[ids_detect["expired_card"] - 1],
        number=info_list[ids_detect["school"] - 2],
    )


def make_card_neu2(info_list):
    ids_detect = detect_info(CardNEU2.get_detect_guide(), info_list)
    id_birth, birth = None, None
    for id_info, info in enumerate(info_list):
        match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", info)
        if match:
            id_birth, birth = id_info, match.group(0)
    if birth is None:
        raise CustomHTTPException(
            error_type="detect_info_failure",
            message=f"birth not found",
        )
    return CardNEU2(
        school=info_list[ids_detect["school"]],
        major=info_list[id_birth + 1],
        fullname=info_list[ids_detect["fullname"] + 1],
        birth=birth,
        expired_card=info_list[ids_detect["expired_card"]],
        number=info_list[ids_detect["number"]],
    )

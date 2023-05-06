import re
from pydantic import BaseModel, root_validator
from unidecode import unidecode
from datetime import datetime

from app.core.exception import CustomHTTPException
from app.util.mail import is_valid_email


class Card(BaseModel):
    school: str
    major: str
    fullname: str
    birth: str
    expired_card: str
    number: str


class CardHUST(Card):
    @root_validator
    def make_card(cls, values):
        print(values)
        if values.get("school", "") != CardHUST.get_detect_guide()["school"]:
            raise CustomHTTPException(error_type="detect_not_support")
        try:
            datetime.strptime(values.get("expired_card", ""), "%d/%m/%Y")
        except ValueError:
            raise CustomHTTPException(
                error_type="detect_info_failure",
                message=f'expired_card:{values.get("expired_card", "")}',
            )
        try:
            datetime.strptime(values.get("birth", ""), "%d/%m/%Y")
        except ValueError:
            raise CustomHTTPException(
                error_type="detect_info_failure",
                message=f'birth:{values.get("birth", "")}',
            )
        if datetime.today() > datetime.strptime(
            values.get("expired_card", "1/1/2000"), "%d/%m/%Y"
        ):
            raise CustomHTTPException(error_type="detect_out_of_date")
        if not values.get("number", "").isdigit():
            raise CustomHTTPException(
                error_type="detect_info_failure",
                message=f'number:{values.get("number", "")}',
            )
        # Tạo email dựa trên thông tin trong values
        fullname = values.get("fullname", "")
        number = values.get("number", "")
        name_parts = unidecode(fullname).lower().split()
        email = (
            name_parts[-1]
            + "."
            + "".join([item[0] for item in name_parts[:-1]])
            + number[2:]
            + "@sis.hust.edu.vn"
        )
        values["email"] = email
        return values

    @classmethod
    def get_detect_guide(self):
        return {
            "school": "HANOI UNIVERSITY OF SCIENCE AND TECHNOLOGY",
            "fullname": "Họ tên / Name",
            "birth": "Ngày sinh / Date of Birth",
            "expired_card": "Giá trị đến / Valid Thru",
            "number": "MSSV / ID No.",
        }


class CardHUCE(Card):
    email: str
    major_class: str

    @root_validator
    def make_card(cls, values):
        print(values)
        try:
            values["major"] = values["major"].split("Faculty.")[-1].strip()
            values["expired_card"] = re.findall(r"\d+", values["expired_card"])[-1]
            values["number"] = re.findall(r"\d+", values["number"])[-1]
            values["email"] = values["email"].split("Email:")[-1].strip()
            values["major_class"] = values["major_class"].split("Class:")[-1].strip()
        except Exception as e:
            raise CustomHTTPException(error_type="detect_invalid", message=str(e))
        if values.get("school", "") != CardHUCE.get_detect_guide()["school"]:
            raise CustomHTTPException(error_type="detect_not_support")
        try:
            datetime.strptime(values.get("birth", ""), "%d/%m/%Y")
        except ValueError:
            raise CustomHTTPException(
                error_type="detect_info_failure",
                message=f'birth:{values.get("birth", "")}',
            )
        if not values.get("expired_card", "").isdigit():
            raise CustomHTTPException(
                error_type="detect_out_of_date",
                message=f'expired_card:{values.get("expired_card", "")}',
            )
        if datetime.now().year > int(values.get("expired_card")):
            raise CustomHTTPException(error_type="detect_out_of_date")
        if not is_valid_email(values.get("email", "")):
            raise CustomHTTPException(error_type="mail_invalid")
        if not values.get("number", "").isdigit():
            raise CustomHTTPException(
                error_type="detect_info_failure",
                message=f'number:{values.get("number", "")}',
            )
        return values

    @classmethod
    def get_detect_guide(self):
        return {
            "school": "NATIONAL UNIVERSITY OF CIVIL ENGINEERING",
            "major": "Khoa / Faculty.",
            "expired_card": "Khóa học / Course: 20-20",
            "number": "MSSV / ID No.",
            "email": "Email: @nuce.edu.vn",
            "major_class": "Lớp / Class:",
        }


class CardNEU(Card):
    @root_validator
    def make_card(cls, values):
        print(values)
        try:
            values["major"] = values["major"].split(":")[-1].strip()
            values["fullname"] = values["fullname"].split(":")[-1].strip()
            values["birth"] = values["birth"].split(":")[-1].strip()
            values["expired_card"] = re.findall(r"\d+", values["expired_card"])[-1]
            values["number"] = re.findall(r"\d+", values["number"])[-1]
            values["email"] = values["number"] + "@st.neu.edu.vn"
        except Exception as e:
            raise CustomHTTPException(error_type="detect_invalid", message=str(e))
        if values.get("school", "") != CardNEU.get_detect_guide()["school"]:
            raise CustomHTTPException(error_type="detect_not_support")
        try:
            datetime.strptime(values.get("birth", ""), "%d/%m/%Y")
        except ValueError:
            raise CustomHTTPException(
                error_type="detect_info_failure",
                message=f'birth:{values.get("birth", "")}',
            )
        if not values.get("expired_card", "").isdigit():
            raise CustomHTTPException(
                error_type="detect_out_of_date",
                message=f'expired_card:{values.get("expired_card", "")}',
            )
        if datetime.now().year > int(values.get("expired_card")):
            raise CustomHTTPException(error_type="detect_out_of_date")
        if not values.get("number", "").isdigit():
            raise CustomHTTPException(
                error_type="detect_info_failure",
                message=f'number:{values.get("number", "")}',
            )
        return values

    @classmethod
    def get_detect_guide(self):
        return {
            "school": "TRƯỜNG ĐẠI HỌC KINH TẾ QUỐC DÂN",
            "fullname": "THẺ SINH VIÊN",
            "expired_card": "Hiệu lực từ : / 20",
        }


if __name__ == "__main__":
    card = CardHUCE(
        school="NATIONAL UNIVERSITY OF CIVIL ENGINEERING",
        major="Khoa / Faculty. aaaa",
        expired_card="Khóa học / Course: 2011-2033",
        number="MSSV / ID No. 123123",
        email="Email: fffff@nuce.edu.vn",
        major_class="Lớp / Class: sdf",
        fullname="tran cong hoang",
        birth="1/2/2003",
    )
    print()
    print(card.__dict__)

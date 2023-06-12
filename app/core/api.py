from app.core.constant import Role


class BaseAPIModel:
    @property
    def ALL(self):
        lst_api = [
            v for v in self.__class__.__dict__.values() if v not in ["__main__", None]
        ]
        return lst_api


class DetectAPI(BaseAPIModel):
    pass


class AccountApi(BaseAPIModel):
    LOGIN = "/account/login"
    LOGIN_FIREBASE = "/account/login-firebase"
    REGISTER = "/account/register"
    ABOUT_ME = "/account/me"
    ACTIVE = "/account/active"
    GET_ALL = "/account/get-all"
    GET = "/account/get"
    UPDATE_PROFILE = "/account/update"
    DISABLE_ACCOUNT = "/account/disable"
    UPDATE_PASSWORD = "/account/update-password"
    NOTIFICATION = "/account/notification"
    RESET_PASSWORD = "/account/reset-password"
    VERIFY = "/account/verify"


class ClusterApi(BaseAPIModel):
    VECTORIZE = "/cluster/vectorize"
    CLUSTERING = "/cluster/clustering"


class ImageApi(BaseAPIModel):
    GET = "/image/get"


ALLOW_ALL = ["*"]

API_PERMISSION = {
    AccountApi.LOGIN: ALLOW_ALL,
    AccountApi.RESET_PASSWORD: ALLOW_ALL,
    AccountApi.LOGIN_FIREBASE: ALLOW_ALL,
    AccountApi.REGISTER: ALLOW_ALL,
    AccountApi.ABOUT_ME: [Role.ADMIN, Role.USER],
    AccountApi.ACTIVE: ALLOW_ALL,
    AccountApi.VERIFY: ALLOW_ALL,
    AccountApi.GET_ALL: [Role.ADMIN, Role.USER],
    AccountApi.GET: [Role.ADMIN, Role.USER],
    AccountApi.UPDATE_PROFILE: [Role.ADMIN, Role.USER],
    AccountApi.NOTIFICATION: [Role.ADMIN, Role.USER],
    AccountApi.DISABLE_ACCOUNT: [Role.ADMIN],
    ClusterApi.VECTORIZE: ALLOW_ALL,
    ClusterApi.CLUSTERING: ALLOW_ALL,
    ImageApi.GET: ALLOW_ALL,
}

WHITE_LIST_PATH = [
    AccountApi.LOGIN,
]

WHITE_LIST_IP = []


def get_permissions(role: str):
    lst_permissions = []
    for api, accepted_role in API_PERMISSION.items():
        if accepted_role == ALLOW_ALL or role in accepted_role:
            lst_permissions.append(api)
    return lst_permissions


if __name__ == "__main__":
    first_elements = set()  # Tạo một set để lưu trữ các phần tử duy nhất

    for path in API_PERMISSION:
        elements = path.split("/")  # Tách chuỗi theo dấu "/"
        first_element = elements[1]  # Lấy phần tử đầu tiên sau dấu "/"
        first_elements.add(first_element)  # Thêm phần tử vào set

    result = list(first_elements)
    print(result)

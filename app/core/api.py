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
    UPDATE_PROFILE = "/account/update"
    DISABLE_ACCOUNT = "/account/disable"
    UPDATE_PASSWORD = "/account/update-password"


ALLOW_ALL = ["*"]

API_PERMISSION = {
    AccountApi.LOGIN: ALLOW_ALL,
    AccountApi.LOGIN_FIREBASE: ALLOW_ALL,
    AccountApi.REGISTER: ALLOW_ALL,
    AccountApi.ABOUT_ME: [Role.ADMIN, Role.USER],
    AccountApi.ACTIVE: ALLOW_ALL,
    AccountApi.GET_ALL: [Role.ADMIN],
    AccountApi.UPDATE_PROFILE: [Role.ADMIN, Role.USER],
    AccountApi.DISABLE_ACCOUNT: [Role.ADMIN],
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

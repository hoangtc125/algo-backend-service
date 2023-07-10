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


class ClubApi(BaseAPIModel):
    CLUB_GET = "/club/get"
    CLUB_CREATE = "/club/create"
    CLUB_UPDATE = "/club/update"
    CLUB_DELETE = "/club/delete"
    CLUB_GETALL = "/club/get-all"
    GROUP_GET = "/club/group/get"
    GROUP_CREATE = "/club/group/create"
    GROUP_UPDATE = "/club/group/update"
    GROUP_DELETE = "/club/group/delete"
    GROUP_GETALL = "/club/group/get-all"
    MEMBER_GET = "/club/member/get"
    MEMBER_CREATE = "/club/member/create"
    MEMBER_UPDATE = "/club/member/update"
    MEMBER_UPDATE_GROUP = "/club/member/update-group"
    MEMBER_DELETE = "/club/member/delete"
    MEMBER_GETALL = "/club/member/get-all"
    FOLLOW_GET = "/club/follow/get"
    FOLLOW_CREATE = "/club/follow/create"
    FOLLOW_UPDATE = "/club/follow/update"
    FOLLOW_DELETE = "/club/follow/delete"
    FOLLOW_GETALL = "/club/follow/get-all"


class RecruitApi(BaseAPIModel):
    CHECK_PERMISSION = "/recruit/check"
    EVENT_GET = "/recruit/event/get"
    EVENT_CREATE = "/recruit/event/create"
    EVENT_UPDATE = "/recruit/event/update"
    EVENT_DELETE = "/recruit/event/delete"
    EVENT_GETALL = "/recruit/event/get-all"
    ROUND_GET = "/recruit/round/get"
    ROUND_CREATE = "/recruit/round/create"
    ROUND_UPDATE = "/recruit/round/update"
    ROUND_DELETE = "/recruit/round/delete"
    ROUND_GETALL = "/recruit/round/get-all"
    PARTICIPANT_GET = "/recruit/participant/get"
    PARTICIPANT_CREATE = "/recruit/participant/create"
    PARTICIPANT_UPDATE = "/recruit/participant/update"
    PARTICIPANT_DELETE = "/recruit/participant/delete"
    PARTICIPANT_GETALL = "/recruit/participant/get-all"
    FORM_QUESTION_GET = "/recruit/form-question/get"
    FORM_QUESTION_CREATE = "/recruit/form-question/create"
    FORM_QUESTION_UPDATE = "/recruit/form-question/update"
    FORM_QUESTION_DELETE = "/recruit/form-question/delete"
    FORM_QUESTION_GETALL = "/recruit/form-question/get-all"
    FORM_ANSWER_GET = "/recruit/form-answer/get"
    FORM_ANSWER_CREATE = "/recruit/form-answer/create"
    FORM_ANSWER_UPDATE = "/recruit/form-answer/update"
    FORM_ANSWER_DELETE = "/recruit/form-answer/delete"
    FORM_ANSWER_GETALL = "/recruit/form-answer/get-all"
    SHIFT_GET = "/recruit/shift/get"
    SHIFT_CREATE = "/recruit/shift/create"
    SHIFT_UPDATE = "/recruit/shift/update"
    SHIFT_DELETE = "/recruit/shift/delete"
    SHIFT_GETALL = "/recruit/shift/get-all"
    APPOINTMENT_GET = "/recruit/appointment/get"
    APPOINTMENT_CREATE = "/recruit/appointment/create"
    APPOINTMENT_UPDATE = "/recruit/appointment/update"
    APPOINTMENT_DELETE = "/recruit/appointment/delete"
    APPOINTMENT_GETALL = "/recruit/appointment/get-all"
    CLUSTER_GET = "/recruit/cluster/get"
    CLUSTER_CREATE = "/recruit/cluster/create"
    CLUSTER_UPDATE = "/recruit/cluster/update"
    CLUSTER_DELETE = "/recruit/cluster/delete"
    CLUSTER_GETALL = "/recruit/cluster/get-all"
    END_FORM_ROUND = "/recruit/round/form/end"
    SEND_SHFIT_MAIL = "/recruit/shift/mail"
    SPLIT_INTERVIEW = "/recruit/interview/split"


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
    AccountApi.GET_ALL: ALLOW_ALL,
    AccountApi.GET: ALLOW_ALL,
    AccountApi.UPDATE_PROFILE: [Role.ADMIN, Role.USER],
    AccountApi.NOTIFICATION: [Role.ADMIN, Role.USER],
    AccountApi.DISABLE_ACCOUNT: [Role.ADMIN],
    ClusterApi.VECTORIZE: ALLOW_ALL,
    ClusterApi.CLUSTERING: ALLOW_ALL,
    ClubApi.CLUB_GET: ALLOW_ALL,
    ClubApi.CLUB_CREATE: [Role.ADMIN, Role.USER],
    ClubApi.CLUB_UPDATE: [Role.ADMIN, Role.USER],
    ClubApi.CLUB_DELETE: [Role.ADMIN, Role.USER],
    ClubApi.CLUB_GETALL: ALLOW_ALL,
    ClubApi.GROUP_GET: ALLOW_ALL,
    ClubApi.GROUP_CREATE: [Role.ADMIN, Role.USER],
    ClubApi.GROUP_UPDATE: [Role.ADMIN, Role.USER],
    ClubApi.GROUP_DELETE: [Role.ADMIN, Role.USER],
    ClubApi.GROUP_GETALL: ALLOW_ALL,
    ClubApi.MEMBER_GET: ALLOW_ALL,
    ClubApi.MEMBER_CREATE: [Role.ADMIN, Role.USER],
    ClubApi.MEMBER_UPDATE: [Role.ADMIN, Role.USER],
    ClubApi.MEMBER_UPDATE_GROUP: [Role.ADMIN, Role.USER],
    ClubApi.MEMBER_DELETE: [Role.ADMIN, Role.USER],
    ClubApi.MEMBER_GETALL: ALLOW_ALL,
    ClubApi.FOLLOW_GET: ALLOW_ALL,
    ClubApi.FOLLOW_CREATE: [Role.ADMIN, Role.USER],
    ClubApi.FOLLOW_UPDATE: [Role.ADMIN, Role.USER],
    ClubApi.FOLLOW_DELETE: [Role.ADMIN, Role.USER],
    ClubApi.FOLLOW_GETALL: ALLOW_ALL,
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

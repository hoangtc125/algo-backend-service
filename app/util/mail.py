import re
from typing import List, Dict


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


class EmailContent:
    def __init__(self) -> None:
        self.content = []

    def h1(self, text):
        self.content.append(f"<h1>{text}</h1>")
        return self

    def h2(self, text):
        self.content.append(f"<h2>{text}</h2>")
        return self

    def h3(self, text):
        self.content.append(f"<h3>{text}</h3>")
        return self

    def h4(self, text):
        self.content.append(f"<h4>{text}</h4>")
        return self

    def h5(self, text):
        self.content.append(f"<h5>{text}</h5>")
        return self

    def h6(self, text):
        self.content.append(f"<h6>{text}</h6>")
        return self

    def a(self, link, text):
        self.content.append(f"<a href='{link}' target='_blank'>{text}</a>")
        return self

    def img(self, base64):
        self.content.append(f"<img src='data:image/png;base64,{base64}'/>")
        return self

    def p(self, text):
        self.content.append(f"<p>{text}</p>")
        return self

    def strong(self, text):
        self.content.append(f"<strong>{text}</strong>")
        return self

    def em(self, text):
        self.content.append(f"<em>{text}</em>")
        return self

    def br(self):
        self.content.append("<br><br>")
        return self

    def ul(self, data: List):
        self.content.append(
            f"<ul>{''.join([f'<li>{item}</li>' for item in data])}</ul>"
        )
        return self

    def ol(self, data: List):
        self.content.append(
            f"<ol>{''.join([f'<li>{item}</li>' for item in data])}</ol>"
        )
        return self

    def table(self, data: Dict):
        self.content.append(
            f"<table>{''.join([f'<tr><td><strong>{k}</strong></td><td><em>{v}</em></td></tr>' for k, v in data.items()])}</table>"
        )
        return self

    def make_html(self):
        return f"<html><body>{''.join([item for item in self.content])}</body></html>"


def make_mail_content_card(card: Dict):
    return (
        EmailContent()
        .h4("Chào bạn,")
        .p(
            "Email này để thông báo cho bạn về kết quả xác thực tài khoản của bạn. Tài khoản của bạn đã được xác thực thành công. Dưới đây là chi tiết xác thực của bạn:"
        )
        .table(card)
        .p(
            "Hãy kiểm tra lại thông tin và xác nhận bằng cách click vào đường link sau: "
        )
        .a("https://chinhphu.vn/", "Đồng ý xác thực tài khoản")
        .p("Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi.")
        .p("Trân trọng,")
        .p("Ban quản trị.")
        .make_html()
    )


def make_mail_active_account(url):
    return (
        EmailContent()
        .h4("Chào bạn,")
        .p(
            "Chúng tôi rất vui mừng thông báo rằng bạn đã đăng ký thành công tài khoản trên hệ thống của chúng tôi. Để hoàn tất quá trình đăng ký và kích hoạt tài khoản, bạn vui lòng thực hiện các bước sau:"
        )
        .ol(
            [
                "Truy cập vào đường dẫn để kích hoạt tài khoản của bạn",
                "Sau khi nhấp vào liên kết kích hoạt, tài khoản của bạn sẽ được kích hoạt và bạn sẽ có thể đăng nhập vào hệ thống bằng thông tin đăng nhập đã đăng ký.",
            ]
        )
        .p("Đường dẫn: ")
        .a(url, "Kích hoạt tài khoản")
        .p(
            "Nếu bạn không thực hiện việc kích hoạt này, tài khoản của bạn sẽ không hoạt động và sẽ bị xóa sau một khoảng thời gian nhất định."
        )
        .p(
            "Nếu bạn gặp bất kỳ vấn đề hoặc câu hỏi nào, vui lòng liên hệ với chúng tôi qua: "
        )
        .a("https://chinhphu.vn/", "Thông tin liên hệ")
        .p(
            "Cảm ơn bạn đã tham gia và chúc bạn có trải nghiệm tuyệt vời trên hệ thống của chúng tôi!"
        )
        .p("Trân trọng,")
        .p("Ban quản trị.")
        .make_html()
    )


if __name__ == "__main__":
    print(is_valid_email("hoang.tc194060@sis.hust.edu.vn"))

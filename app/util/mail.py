import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Dict

from app.core.config import project_config
from app.core.exception import CustomHTTPException


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


class Email:
    def __init__(
        self,
        receiver_email: str,
        subject: str,
        content: EmailContent,
        cc_email: List = [],
    ) -> None:
        if not is_valid_email(receiver_email):
            raise CustomHTTPException(error_type="mail_invalid")
        self.receiver_email = receiver_email
        self.message = MIMEMultipart()
        self.message["From"] = Header(project_config.MAIL_USER, "utf-8")
        self.message["To"] = Header(receiver_email, "utf-8")
        self.message["Cc"] = ", ".join(cc_email)
        self.message["Subject"] = Header(subject, "utf-8")
        self.message.attach(MIMEText(content, "html", "utf-8"))


def send_mail(email: Email):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(project_config.MAIL_USER, project_config.MAIL_PASS)
        server.sendmail(
            project_config.MAIL_USER,
            email.receiver_email,
            email.message.as_string(),
        )
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)
    finally:
        server.quit()


def send_many_mail(emails: List[Email]):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(project_config.MAIL_USER, project_config.MAIL_PASS)

        for email in emails:
            try:
                server.sendmail(
                    project_config.MAIL_USER,
                    email.receiver_email,
                    email.message.as_string(),
                )
                print("Email sent to", email.receiver_email)
            except Exception as e:
                print("Error sending email to", email.receiver_email, ":", e)

        server.quit()

        print("All emails sent successfully!")
    except Exception as e:
        print("Error sending emails:", e)


def make_mail_verify_account(card: Dict, url: str):
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
        .a(url, "Đồng ý xác thực tài khoản")
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


def make_mail_reset_password(url):
    return (
        EmailContent()
        .h4("Chào bạn,")
        .p(
            "Bạn nhận được email này vì yêu cầu đặt lại mật khẩu của bạn đã được gửi đến chúng tôi. Để hoàn tất quá trình đặt lại mật khẩu, vui lòng nhấp vào liên kết bên dưới:"
        )
        .a(url, "Liên kết đặt lại mật khẩu")
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


def make_mail_welcome():
    return (
        EmailContent()
        .h4("Xin chào,")
        .p(
            "Chúng tôi chân thành chào mừng bạn đến với hệ thống của chúng tôi! Đây là một thư gửi tự động để thông báo rằng tài khoản của bạn đã được tạo thành công."
        )
        .p(
            "Cảm ơn bạn đã tham gia và tin tưởng sử dụng dịch vụ của chúng tôi. Chúng tôi cam kết cung cấp cho bạn trải nghiệm tuyệt vời và hỗ trợ tốt nhất."
        )
        .p(
            "Nếu bạn có bất kỳ câu hỏi hoặc yêu cầu hỗ trợ nào, đừng ngần ngại liên hệ với chúng tôi. Chúng tôi luôn sẵn lòng giúp đỡ bạn."
        )
        .p("Một lần nữa, chào mừng bạn đến với hệ thống của chúng tôi!")
        .p("Trân trọng,")
        .p("Ban quản trị.")
        .make_html()
    )


def make_mail_end_form_round(club_name: str, participant_name: str, res: bool):
    return (
        EmailContent()
        .h4("Kính gửi Anh/Chị,")
        .p(
            f"{club_name} xin trân trọng thông báo kết quả vòng đơn ứng tuyển thành viên của Anh/Chị. Sau quá trình xem xét và đánh giá kỹ lưỡng, chúng tôi xin thông báo kết quả như sau:"
        )
        .p(
            f"- Anh/Chị {participant_name}: {res} (True: Được chọn, False: Không được chọn)"
        )
        .p(
            f"Chúng tôi xin cảm ơn Anh/Chị đã quan tâm và tham gia quá trình ứng tuyển thành viên của {club_name}. Nếu Anh/Chị không được chọn, xin đừng nản lòng và hãy tiếp tục theo đuổi đam mê của mình. Nếu Anh/Chị đã được chọn, chúng tôi sẽ liên hệ trong thời gian sớm nhất để thông báo các bước tiếp theo."
        )
        .p(
            f"Một lần nữa, xin chân thành cảm ơn Anh/Chị đã dành thời gian và quan tâm đến CLB!"
        )
        .p("Trân trọng,")
        .p("Ban quản trị.")
        .make_html()
    )


def make_shift_mail(club_name: str, participant_name: str, link: str):
    return (
        EmailContent()
        .h4(f"Kính gửi {participant_name},")
        .p(
            f"Chúng tôi xin gửi lời mời cho bạn để tham gia khảo sát nguyện vọng phỏng vấn vào {club_name}"
        )
        .p(
            f"Đây là một bước quan trọng trong quá trình tuyển dụng của chúng tôi và chúng tôi rất mong nhận được phản hồi từ bạn. Hãy dành chút thời gian để điền khảo sát này để chúng tôi có thể hiểu rõ hơn về nguyện vọng và kỹ năng của bạn."
        )
        .p(f"Vui lòng truy cập vào đường dẫn dưới đây để bắt đầu điền khảo sát")
        .a(link, "Yêu cầu điền khảo sát nguyện vọng phỏng vấn")
        .p(
            f"Một lần nữa, xin chân thành cảm ơn Anh/Chị đã dành thời gian và quan tâm đến CLB!"
        )
        .p("Trân trọng,")
        .p("Ban quản trị.")
        .make_html()
    )


def make_mail_interview(club_name: str, participant_name: str, value: str):
    return (
        EmailContent()
        .h4(f"Kính gửi {participant_name},")
        .p(
            f"Chúng tôi xin gửi lời chào tới bạn và xin cảm ơn bạn đã quan tâm đến câu lạc bộ của chúng tôi. Chúng tôi đã xem xét thông tin đăng ký của bạn và rất vui thông báo rằng bạn đã được chọn để tham gia buổi phỏng vấn tại câu lạc bộ {club_name}"
        )
        .p(f"Dưới đây là thông tin chi tiết về buổi phỏng vấn: {value}")
        .p(
            f"Xin vui lòng đến đúng giờ và chuẩn bị các tài liệu, hồ sơ hoặc bất kỳ vật phẩm liên quan nào mà bạn cho là cần thiết để trình bày và thảo luận về kinh nghiệm, kỹ năng và sự quan tâm của bạn đối với câu lạc bộ."
        )
        .p(
            f"Trong buổi phỏng vấn, chúng tôi sẽ tiến hành một cuộc trò chuyện cá nhân với bạn để hiểu rõ hơn về khả năng, mục tiêu và đóng góp mà bạn có thể mang đến cho câu lạc bộ. Chúng tôi cũng sẽ cung cấp thông tin chi tiết về câu lạc bộ, hoạt động và mong đợi của chúng tôi từ các ứng viên."
        )
        .p(
            "Rất mong được gặp bạn trong buổi phỏng vấn và cùng trao đổi về cơ hội tham gia vào câu lạc bộ. Nếu bạn có bất kỳ câu hỏi hoặc yêu cầu nào khác, xin đừng ngần ngại liên hệ với chúng tôi qua email hoặc số điện thoại dưới đây."
        )
        .p("Trân trọng,")
        .p("Ban quản trị.")
        .make_html()
    )


if __name__ == "__main__":
    print(is_valid_email("hoang.tc194060@sis.hust.edu.vn"))

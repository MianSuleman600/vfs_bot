import smtplib
from email.message import EmailMessage

class EmailClient:
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.host = smtp_host
        self.port = smtp_port
        self.user = username
        self.pwd = password

    def send(self, to_addr: str, subject: str, body: str):
        msg = EmailMessage()
        msg['From'] = self.user
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.user, self.pwd)
            server.send_message(msg)
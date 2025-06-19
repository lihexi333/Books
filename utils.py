import smtplib
from email.mime.text import MIMEText
import os

def send_email(to_email, subject, content):
    MAIL_HOST = os.environ.get('MAIL_HOST', 'smtp.qq.com')
    MAIL_USER = os.environ.get('MAIL_USER', 'your_qq_email@qq.com')
    MAIL_PASS = os.environ.get('MAIL_PASS', 'your_email_password')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = MAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    try:
        server = smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT)
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(MAIL_USER, [to_email], msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}") 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from root.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD

def send_password_reset_email(to_email, reset_link):
    subject = "Password Reset Request"
    body = f"""
    Hello,

    You have requested to reset your password. Please click on the link below to reset your password:

    {reset_link}

    If you did not request this, please ignore this email.

    Best regards,
    Your Application Team
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        print(f"Password reset email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

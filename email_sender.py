import os
import smtplib
from email.message import EmailMessage


def send_certificate_email(
    recipient,
    subject,
    body,
    attachment_path
):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_host or not smtp_user or not smtp_password:
        return (
            False,
            "Email service is not configured."
        )

    if not os.path.exists(attachment_path):
        return (
            False,
            "Certificate file was not found."
        )

    try:
        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = smtp_user
        message["To"] = recipient

        message.set_content(body)

        with open(attachment_path, "rb") as file:
            data = file.read()

        message.add_attachment(
            data,
            maintype="application",
            subtype="octet-stream",
            filename=os.path.basename(
                attachment_path
            )
        )

        with smtplib.SMTP(
            smtp_host,
            smtp_port
        ) as server:

            server.starttls()

            server.login(
                smtp_user,
                smtp_password
            )

            server.send_message(message)

        return (
            True,
            "Certificate email sent successfully."
        )

    except Exception as error:
        return (
            False,
            f"Email sending failed: {error}"
        )
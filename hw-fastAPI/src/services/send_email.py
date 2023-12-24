from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME="app.systems@rusanovka-net.kiev.ua",
    MAIL_PASSWORD="123Qwe",
    MAIL_FROM="app.systems@rusanovka-net.kiev.ua",
    MAIL_PORT=25,
    MAIL_SERVER="mail.rusanovka-net.kiev.ua",
    MAIL_FROM_NAME="Global BASE of Contacts",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email, please",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fast_m = FastMail(conf)
        await fast_m.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
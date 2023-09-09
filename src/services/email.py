from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="PhotoShare Application",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """The send_email function sends an email to the user with a link to confirm their email address.

    The function takes in three arguments:

    - email: the user's email address, which is used as a unique identifier for them.
    - username: the username of the user who is registering. This will be displayed in their confirmation message so they know it was sent to them and not someone else.
    - host: this is where we are hosting our application, which will be used as part of our confirmation link.

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username of the user to be sent in the email
    :param host: str: Pass the hostname of your application to the template
    :return: A coroutine object

    """

    try:
        token_verification = auth_service.create_email_token({"email": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="example_email.html")
    except ConnectionErrors as err:
        print(err)


async def reset_password_by_email(
    email: EmailStr, username: str, reset_token: str, host: str
):
    """Send an email to reset a user's password.

    This function sends an email to the user with a link to reset their account password.

    :param email: EmailStr: The recipient's email address.
    :param username: str: The username of the user receiving the email.
    :param reset_token: str: The password reset token.
    :param host: str: The hostname of your application for the reset link.
    """
    try:
        message = MessageSchema(
            subject="Reset account ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": reset_token},
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)

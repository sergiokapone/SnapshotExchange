from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)

from pydantic import EmailStr
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.services.email import send_email, reset_password_by_email
from src.database.connect_db import get_db
from src.schemas import UserSchema, UserResponseSchema, TokenSchema, RequestEmail, MessageResponseSchema
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.messages import (
    ALREADY_EXISTS,
    ALREADY_EXISTS_EMAIL,
    ALREADY_EXISTS_USERNAME,
    EMAIL_ALREADY_CONFIRMED,
    EMAIL_CONFIRMED,
    EMAIL_NOT_CONFIRMED,
    INVALID_EMAIL,
    INVALID_PASSWORD,
    INVALID_TOKEN,
    SUCCESS_CREATE_USER,
    VERIFICATION_ERROR,
    CHECK_YOUR_EMAIL,
    USER_NOT_ACTIVE,
    USER_IS_LOGOUT,
    EMAIL_HAS_BEEN_SEND,
    PASWORD_RESET_SUCCESS,
)

from src.conf.constants import TOKEN_LIFE_TIME


router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post(
    "/signup",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    body: UserSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    exist_user_email = await repository_users.get_user_by_email(body.email, session)
    exist_user_username = await repository_users.get_user_by_username(
        body.username, session
    )

    if exist_user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ALREADY_EXISTS_EMAIL
        )

    if exist_user_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ALREADY_EXISTS_USERNAME
        )

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, session)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {"user": new_user, "detail": SUCCESS_CREATE_USER}


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    The login function is used to authenticate a user.

    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Pass the database session to the function
    :return: A dict with the access_token, refresh_token and token type
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=EMAIL_NOT_CONFIRMED
        )
    # Check is_active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=USER_NOT_ACTIVE
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_PASSWORD
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(
        data={"email": user.email}, expires_delta=TOKEN_LIFE_TIME
    )
    refresh_token = await auth_service.create_refresh_token(data={"email": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", response_model=MessageResponseSchema)
async def logout(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_authenticated_user),
):
    token = credentials.credentials

    await repository_users.add_to_blacklist(token, db)
    return {"message": USER_IS_LOGOUT}


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_authenticated_user),
):
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns an access_token, a new refresh_token, and the type of token (bearer).

    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Pass the database session to the function
    :return: A dictionary with the access_token, refresh_token and token_type
    """
    token = credentials.credentials
    email = await auth_service.decode_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN
        )

    access_token = await auth_service.create_access_token(data={"email": email})
    refresh_token = await auth_service.create_refresh_token(data={"email": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}", response_model=MessageResponseSchema)
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes in the token that was sent to the user's email and uses it to get their email address.
        Then, it gets the user from our database using their email address and checks if they exist. If not, an error is thrown.
        Next, we check if they have already confirmed their account by checking if confirmed = True for them in our database (if so, an error is thrown).
        Finally, we set confirmed = True for them in our database.

    :param token: str: Get the token from the url
    :param db: Session: Get the database connection
    :return: A dictionary with the message &quot;email confirmed&quot;
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=VERIFICATION_ERROR
        )
    if user.confirmed:
        return {"message": EMAIL_ALREADY_CONFIRMED}
    await repository_users.confirm_email(email, db)
    return {"message": EMAIL_CONFIRMED}


@router.post("/request_email", response_model=MessageResponseSchema)
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to verify their account. The function takes in a RequestEmail object, which contains the email of
    the user who wants to verify their account. It then checks if there is already an existing user with
    that email address and if they have already verified their account. If not, it sends them an email
    with a link that will allow them to do so.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A message that the email has been sent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user and user.confirmed:
        return {"message": EMAIL_CONFIRMED}

    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": CHECK_YOUR_EMAIL}


@router.post("/forgot_password", response_model=MessageResponseSchema)
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_201_CREATED, detail=EMAIL_HAS_BEEN_SEND
        )

    # Generate a password reset token
    data = {"email": email}
    reset_token = auth_service.create_email_token(data)

    background_tasks.add_task(
        reset_password_by_email, email, user.username, reset_token, request.base_url
    )

    return {"message": EMAIL_HAS_BEEN_SEND}


@router.post("/reset_password", response_model=MessageResponseSchema)
async def reset_password(
    reset_token: str, new_password: str, db: AsyncSession = Depends(get_db)
):
    email = await auth_service.get_email_from_token(reset_token)

    # Обновляем пароль пользователя
    user = await repository_users.get_user_by_email(email, db)
    user.password = auth_service.get_password_hash(new_password)

    # Сохраняем изменения в базе данных
    await db.commit()

    return {"message": PASWORD_RESET_SUCCESS}

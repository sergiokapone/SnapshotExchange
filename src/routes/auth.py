### Import from FastAPI ###

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)

from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)


### Import from SQLAlchemy ###

from sqlalchemy.ext.asyncio import AsyncSession

### Import from Pydentic ###

from pydantic import EmailStr

### Import from Configurations ###


from src.conf.messages import (
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

### Import from Database ###

from src.database.models import User
from src.database.connect_db import get_db

### Import from Schemas ###

from src.schemas import (
    UserSchema,
    TokenSchema,
    RequestEmail,
    MessageResponseSchema,
)

### Import from Services ###

from src.services.email import send_email, reset_password_by_email
from src.services.auth import auth_service

### Import from Repository ###

from src.repository import users as repository_users


router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post(
    "/signup",
    name="signup",
    description="Root is designed for user registration",
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    body: UserSchema,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    # Register a new user.

    This route allows you to register a new user.

    Level of Access:

    - All comers


    :param body: UserSchema: New user data.

    :param background_tasks: BackgroundTasks: Tasks to be performed in the background.

    :param request: Request: Inquiry.

    :param session: AsyncSession: Database Session.

    :return: New user data and a message about successful registration.

    :raises: HTTPException with code 409 and detail "ALREADY_EXISTS_EMAIL" or "ALREADY_EXISTS_USERNAME" if a user with that email or username already exists.

    """

    exist_user_email = await repository_users.get_user_by_email(body.email, db)
    exist_user_username = await repository_users.get_user_by_username(body.username, db)

    if exist_user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ALREADY_EXISTS_EMAIL
        )

    if exist_user_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ALREADY_EXISTS_USERNAME
        )

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {"user": new_user, "detail": SUCCESS_CREATE_USER}


@router.post("/login", response_model=TokenSchema)
async def login(
    # response:Response,
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Log in and get access tokens.

    This route allows the user to log in by providing the correct email and password and receive access tokens.

    Level of Access:

    - Verified users

    :param body: OAuth2PasswordRequestForm: A form with the user's email and password.

    :param db: AsyncSession: Database Session.

    :return: Access tokens (access_token and refresh_token).

    :rtype: TokenSchema

    :raises: HTTPException with codes 401 or 403 in case of authentication or activation errors, as well as in case of invalid password.
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

    # response.set_cookie(key=COOKIE_KEY_NAME, value=access_token, httponly=True)

    tokens = TokenSchema(access_token=access_token, refresh_token=refresh_token)

    return tokens


@router.post("/logout", response_model=MessageResponseSchema)
async def logout(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(auth_service.get_authenticated_user),
):
    """
    **Log out user and add the token to the blacklist.**

    This route allows the user to log out and their access token will be added to the blacklist.

    Level of Access:

    - Current authorized user

    :param credentials: HTTPAuthorizationCredentials: User authentication data (token).

    :param db: AsyncSession: Database Session.

    :param current_user: User: Current authenticated user.

    :return: A message informing you that the user has successfully logged out of the system.

    :rtype: MessageResponseSchema
    """

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
    Updates the user's access token.

    This route allows the user's access token to be refreshed if a valid refresh token is present.

    Level of Access:

    - Current authorized user

    :param credentials: HTTPAuthorizationCredentials: User authentication data (access token).

    :param db: AsyncSession: Database session.

    :param current_user: User: Current authenticated user.

    :return: New access tokens (access_token and refresh_token).

    :rtype: TokenSchema

    :raises: HTTPException with code 401 and detail "INVALID_TOKEN" in case of invalid access token.
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
    Confirmation of the user's email.

    This route allows the user to confirm their email by providing the correct confirmation token.

    Level of Access:

    - Users who have registered

    :param token: str: Email confirmation token.

    :param db: AsyncSession: Database session.

    :return: Successful email confirmation message.

    :rtype: MessageResponseSchema

    :raises: HTTPException with code 400 and detail "VERIFICATION_ERROR" in case of invalid token, and also with code 400 and detail "EMAIL_ALREADY_CONFIRMED" in case of already confirmed email.
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
    Request to confirm the user's email.

    This route allows the user to request that an email be sent to confirm the user's email.

    Level of Access:

    - Any user
    - Email is only sent to registered users.

    :param body: RequestEmail: Form with user's email.

    :param background_tasks: BackgroundTasks: Tasks that are running in the background (sending an email).

    :param request: Request: Client request.

    :param db: AsyncSession: Database session.

    :return: Email confirmation request message.

    :rtype: MessageResponseSchema

    :raises: HTTPException with the code 400 and detail "EMAIL_CONFIRMED" in case of already confirmed email.
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
    """
    User password recovery request.

    This route allows the user to request password recovery via email.

    Level of Access:

    - Any user
    - Email is only sent to registered users.

    :param email: EmailStr: Email of the user for whom password recovery is requested.

    :param background_tasks: BackgroundTasks: Tasks that are executed in the background (sending an email with instructions).

    :param request: Request: Client request.

    :param db: AsyncSession: Database session.

    :return: Message that password recovery instructions have been sent to email.

    :rtype: MessageResponseSchema

    :raises: HTTPException with code 201 and detail "EMAIL_HAS_BEEN_SEND" in case of successful password recovery request.
    """

    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_201_CREATED, detail=EMAIL_HAS_BEEN_SEND
        )

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
    """
    Reset user password.

    Level of Access:

    - Any user

    This route allows the user to reset their password by providing the correct reset token and a new password.

    :param reset_token: str: Password reset token.

    :param new_password: str: The user's new password.

    :param db: AsyncSession: Database session.

    :return: Password reset success message.

    :rtype: MessageResponseSchema

    :raises: HTTPException with code 401 and detail "INVALID_TOKEN" in case of invalid token, and with code 401 and detail "PASWORD_RESET_SUCCESS" in case of successful password reset.
    """

    email = await auth_service.get_email_from_token(reset_token)

    user = await repository_users.get_user_by_email(email, db)
    user.password = auth_service.get_password_hash(new_password)

    try:
        await db.commit()
        return {"message": PASWORD_RESET_SUCCESS}
    except Exception as e:
        await db.rollback()
        print(e)

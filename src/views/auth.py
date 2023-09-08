from fastapi import (
    APIRouter,
    Header,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Response,
    Request,
)

from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.requests import Request


### Import from SQLAlchemy ###

from sqlalchemy.ext.asyncio import AsyncSession

### Import from Pydentic ###

from pydantic import EmailStr

### Import from Configurations ###

from src.conf.constants import COOKIE_KEY_NAME

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

### Import from Database ###

from src.database.models import User
from src.database.connect_db import get_db

### Import from Schemas ###

from src.schemas import (
    UserSchema,
    UserResponseSchema,
    TokenSchema,
    RequestEmail,
    MessageResponseSchema,
)

### Import from Services ###
from src.services.auth import auth_service

### Import from Repository ###

from src.repository import users as repository_users


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/auth", tags=["Authentication View"])
security = HTTPBearer()

@router.get("/signup", name='signup_render', include_in_schema=False)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/login", name='login_render', include_in_schema=False)
async def login_page(request: Request):
    """
    Login Page

    This endpoint renders the login page, allowing users to log in from SSR mode.

    :param request: The HTTP request object.
    :type request: Request
    :return: A rendered HTML login page.
    :rtype: templates.TemplateResponse

    **Example Request:**

    .. code-block:: http

        GET /login HTTP/1.1
        Host: yourapi.com

    **Example Response:**

    A rendered HTML login page where users can enter their credentials to log in.
    """
    
    return templates.TemplateResponse("login.html", {"request": request})
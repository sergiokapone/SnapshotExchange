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

@router.get("/login", name='login_render')
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login_form", name="login_form")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    
    # Get the data from the form
    username = form_data.username
    password = form_data.password

    # Perform username and password verification
    user = await repository_users.get_user_by_email(username, db)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not auth_service.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )


    access_token = await auth_service.create_access_token(data={"sub": user.email})
    
    response = RedirectResponse(url=request.url_for("view_all_photos"), status_code=302)
    
    response.set_cookie(key=COOKIE_KEY_NAME, value=access_token, httponly=True)
    
    
    print("->>>>>>>>>>>>>>>>>>---", access_token)
        
    return response
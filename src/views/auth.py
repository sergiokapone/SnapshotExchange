from fastapi import (
    APIRouter,
    Request,
)

from fastapi.security import (
    HTTPBearer,
)

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request


### Import from SQLAlchemy ###


### Import from Pydentic ###


### Import from Configurations ###


### Import from Database ###


### Import from Schemas ###


### Import from Services ###

### Import from Repository ###


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/auth", tags=["Authentication View"])
security = HTTPBearer()


@router.get("/signup", name="signup_render", include_in_schema=False)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/login", name="login_page", include_in_schema=False)
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


@router.get("/forgot_form", name="forgot_form", include_in_schema=False)
async def render_forgot_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

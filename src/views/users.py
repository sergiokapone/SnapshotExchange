from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Query,
    Request,
)

from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

templates = Jinja2Templates(directory="templates")

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect_db import get_db
from src.repository import photos as repository_photos
from src.repository import users as repository_users
from src.repository import ratings as repository_rating


router = APIRouter(tags=["Views"])


@router.get("/view_user_profile/{username}", 
            include_in_schema=False, 
            name="view_user_profile")
async def view_user_profile(
    username: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Получите информацию о пользователе с помощью функции get_user_profile
    user = await repository_users.get_user_profile(username, db)
    
    print(user)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Верните шаблон с информацией о пользователе
    return templates.TemplateResponse(
        "user_profile_page.html", {"request": request, "user": user}
    )

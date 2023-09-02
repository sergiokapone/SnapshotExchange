from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Response,
    Request,
    Header
)


from fastapi.templating import Jinja2Templates
from starlette.requests import Request
templates = Jinja2Templates(directory="templates")  

from fastapi_limiter.depends import RateLimiter

from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import photos as repository_photos
from src.database.models import User, Role
from src.schemas import (
    UserProfile,
    UserProfileSchema,
    UserResponseSchema,
    RequestEmail,
    UserDb,
    RequestRole,
    MessageResponseSchema,
)

from src.schemas import PhotosDb

from src.services.auth import auth_service
from src.services.roles import RoleChecker
from src.conf.messages import (
    NOT_FOUND,
    USER_ROLE_EXISTS,
    INVALID_EMAIL,
    USER_NOT_ACTIVE,
    USER_ALREADY_NOT_ACTIVE,
    USER_CHANGE_ROLE_TO,
    PHOTO_UPLOADED,
    PHOTO_REMOVED
)

from src.services.roles import (
    allowed_get_user,
    allowed_create_user,
    allowed_get_all_users,
    allowed_remove_user,
    allowed_ban_user,
    allowed_change_user_role,
)

router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post("/make_URL_QR/")
async def make_URL_QR(photo_id: int, db: AsyncSession = Depends(get_db)):
    data = await res_photos.get_URL_Qr(photo_id, db)

    return data


@router.post(
    "/photo_test/",
    dependencies=[Depends(allowed_get_user)],
    response_model=MessageResponseSchema,
)
async def test_photo(
    url: str,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    url = await res_photos.created_photo(url, current_user, db)

    return {"message": PHOTO_UPLOADED}

""" ------------------- Crud operations for photos ------------------------ """

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests per minute",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(allowed_get_user),
    ],
    response_model=MessageResponseSchema,
)
async def upload_new_photo(
    photo_file: UploadFile = File(...),
    description: str = Form(None),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseSchema:
    """Upload new photos"""
    if description is not None:
        if len(description) > 500:
            raise HTTPException(
                status_code=400,
                detail="Description is too long. Maximum length is 500 characters.",
            )
        new_photo = await repository_photos.upload_photo(
            current_user, photo_file, description, db
        )
    else:
        new_photo = await repository_photos.upload_photo(current_user, photo_file, db)

    if new_photo:
        return {"message": PHOTO_UPLOADED}

@router.get(
    "/get_all",
    response_model=list[PhotosDb],
    dependencies=[Depends(allowed_get_all_users)],
)
async def read_all_photos(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
) ->list:
    photos = await repository_photos.get_photos(skip, limit, db)
    return photos

@router.get(
    "/get_all/view",
    dependencies=[Depends(allowed_get_all_users), Depends(auth_service.get_authenticated_user)]
)
async def read_all_photos(request: Request,
    skip: int = 0, limit: int = 10,  db: AsyncSession = Depends(get_db), 
    authorization: str = Header(None)
):
    photos = await repository_photos.get_photos(skip, limit, db)
    return templates.TemplateResponse("photo_list.html", {"request": request, "photos": photos})


@router.delete("/{photo_id}", response_model=MessageResponseSchema)
async def remove_photo(
    photo_id: int, 
    current_user: User = Depends(auth_service.get_authenticated_user), 
    db: AsyncSession = Depends(get_db)) -> MessageResponseSchema:

    result = await repository_photos.remove_photo(photo_id, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)

    return  {"message": PHOTO_REMOVED}
      

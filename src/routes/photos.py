from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Response,
)

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
)


router = APIRouter(prefix="/photos", tags=["Photos"])

# Permissions to use routes by role

allowed_get_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_create_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_get_all_users = RoleChecker([Role.admin])
allowed_remove_user = RoleChecker([Role.admin])
allowed_ban_user = RoleChecker([Role.admin])
allowed_change_user_role = RoleChecker([Role.admin])


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

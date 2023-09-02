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
    """
    Generate a QR code URL for a photo.

    This function generates a QR code URL for the specified photo by its ID.

    :param photo_id: int: The ID of the photo for which to generate a QR code URL.
    :param db: AsyncSession: The database session.
    :return: A dictionary containing the QR code URL.
    :rtype: dict
    """
    data = await repository_photos.get_URL_Qr(photo_id, db)

    return data


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
    """
    Upload a new photo.

    This function allows users to upload new photos. It enforces a rate limit of 10 requests per minute. Users must be authenticated
    and have the appropriate role to perform this action. The function accepts an uploaded photo file, an optional description,
    the current authenticated user, and a database session.

    :param photo_file: UploadFile: The photo file to be uploaded.
    :param description: str: An optional description for the photo.
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: A message indicating that the photo has been uploaded.
    :rtype: MessageResponseSchema
    """
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

@router.delete("/{photo_id}", response_model=MessageResponseSchema)
async def remove_photo(
    photo_id: int, 
    current_user: User = Depends(auth_service.get_authenticated_user), 
    db: AsyncSession = Depends(get_db)) -> MessageResponseSchema:
    """
    Remove a photo by its ID.

    This function allows users to remove a photo by its ID. Users must be authenticated and have the appropriate role
    to perform this action. The function accepts the ID of the photo to be removed, the current authenticated user, and a database session.

    :param photo_id: int: The ID of the photo to be removed.
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: A message indicating that the photo has been removed.
    :rtype: MessageResponseSchema
    """

    result = await repository_photos.remove_photo(photo_id, current_user, db)
    print("------>", result)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return  {"message": PHOTO_REMOVED}
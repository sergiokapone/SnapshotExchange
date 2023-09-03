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
    Header,
    Query
)


from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
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
    PHOTO_REMOVED,
    NO_PHOTO_FOUND
)

from src.services.roles import Admin_Moder_User, Admin


router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post("/make_URL_QR/")
async def make_URL_QR(
    photo_id: int,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
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

@router.get("/{username}",
            status_code=status.HTTP_200_OK,
            response_model=dict,
            description="No more than 10 requests per minute",
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def get_all_photos(skip: int = Query(0, description="Number of records to skip"),
                         limit: int = Query(10, description="Number of records to retrieve"),
                         current_user: User = Depends(auth_service.get_authenticated_user),
                         db: AsyncSession = Depends(get_db)):
    """Getting all photos from a database for current user"""
    photos_dict = await repository_photos.get_all_photos(skip, limit, current_user, db)

    if photos_dict:
        return jsonable_encoder(photos_dict)
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_FOUND)

@router.get("/{username}/{photo_id}",
        status_code=status.HTTP_200_OK,
        response_model=dict,
        description="No more than 10 requests per minute",
        dependencies=[Depends(RateLimiter(times=10, seconds=60))]
        )
async def get_one_photo(photo_id: str,
                        current_user: User = Depends(auth_service.get_authenticated_user),
                        db: AsyncSession = Depends(get_db)):
    """Getting a photo for current user by unique photo id"""

    photo = await repository_photos.get_photo_by_id(current_user, photo_id, db)

    if photo:
        return jsonable_encoder(photo)
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_FOUND)
    
@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests per minute",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(Admin_Moder_User),
    ],
    response_model=MessageResponseSchema,
)
async def upload_photo(
    photo_file: UploadFile = File(...),
    description: str | None = Form(None),
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
        new_photo = await repository_photos.upload_photo(
            current_user, photo_file, description, db
        )

    if new_photo:
        return {"message": PHOTO_UPLOADED}
@router.patch("/{username}/{photo_id}",
              status_code=status.HTTP_200_OK,
              description="No more than 10 requests per minute",
              dependencies=[Depends(RateLimiter(times=10, seconds=60))]
              )
async def patch_update_photo(photo_id: str,
                             new_photo_description: str,
                             current_user: User = Depends(auth_service.get_authenticated_user),
                             db: AsyncSession = Depends(get_db)
                             ):
    """Updating a photo by its id"""
    updated_photo = await repository_photos.patch_update_photo(current_user, photo_id, new_photo_description, db)

    if updated_photo:
        return jsonable_encoder(updated_photo)
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_BY_ID)


@router.get(
    "/get_all",
    response_model=list[PhotosDb],
    dependencies=[Depends(Admin)],
)
async def read_all_photos(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
) -> list:
    photos = await repository_photos.get_photos(skip, limit, db)
    return photos


@router.get(
    "/get_all/view",
    dependencies=[
        Depends(Admin),
        Depends(auth_service.get_authenticated_user),
    ],
)
async def read_all_photos(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(None),
):
    photos = await repository_photos.get_photos(skip, limit, db)
    return templates.TemplateResponse(
        "photo_list.html", {"request": request, "photos": photos}
    )


@router.delete("/{photo_id}", response_model=MessageResponseSchema)
async def remove_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseSchema:
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
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return {"message": PHOTO_REMOVED}

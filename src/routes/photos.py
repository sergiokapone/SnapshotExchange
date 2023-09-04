from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Query,
)

from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

templates = Jinja2Templates(directory="templates")

from fastapi_limiter.depends import RateLimiter

from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import photos as repository_photos
from src.database.models import User, Role
from src.schemas import (
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
    USER_ROLE_IN_USE,
    INVALID_EMAIL,
    USER_NOT_ACTIVE,
    USER_ALREADY_NOT_ACTIVE,
    USER_CHANGE_ROLE_TO,
    PHOTO_UPLOADED,
    PHOTO_REMOVED,
    NO_PHOTO_FOUND,
    NO_PHOTO_BY_ID,
    LONG_DESCRIPTION,
)

from src.services.roles import Admin_Moder_User, Admin

router = APIRouter(prefix="/photos", tags=["Photos"])


""" ------------------- Crud operations for photos ------------------------ """


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
    tags: List[str] = Form(None),
    width: int = None,
    height: int = None,
    crop_mode: str = None,
    gravity_mode: str = None,
    rotation_angle: int = None,
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
    :param tags: An optional list of tags. Max number of tags - 5
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: A message indicating that the photo has been uploaded.
    :rtype: MessageResponseSchema
    """
    if description is not None and len(description) > 500:
        raise HTTPException(status_code=400, detail=LONG_DESCRIPTION)

    # check number of tags
    list_tags = tags[0].split(",")
    if len(list_tags) > 5:
        if len(list_tags) > 5:
            raise HTTPException(
                status_code=400, detail="You can't add more than 5 tags to a photo."
            )
    # each tag should have no more than 25 characters
    for tag in list_tags:
        if len(tag) > 25:
            raise HTTPException(
                status_code=400,
                detail="Tag name should be no more than 25 characters long.",
            )

    # uploading a new photo
    new_photo = await repository_photos.upload_photo(
        current_user,
        photo_file,
        description,
        db,
        width,
        height,
        crop_mode,
        gravity_mode,
        rotation_angle,
        list_tags,
    )

    if new_photo:
        return {"message": PHOTO_UPLOADED}


@router.get(
    "/get_all",
    response_model=list[PhotosDb],
    dependencies=[Depends(Admin)],
)
async def get_all_photos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    photos = await repository_photos.get_photos(skip, limit, current_user, db)
    return photos

@router.get(
    "/get_my",
    response_model=list[PhotosDb],
    dependencies=[Depends(Admin)],
)
async def get_all_photos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    photos = await repository_photos.get_my_photos(skip, limit, current_user, db)
    return photos

# @router.get(
#     "/get_all/view",
#     dependencies=[
#         Depends(Admin),
#         Depends(auth_service.get_authenticated_user),
#     ],
# )
# async def get_all_photos(
#     request: Request,
#     skip: int = 0,
#     limit: int = 10,
#     db: AsyncSession = Depends(get_db),
#     authorization: str = Header(None),
# ):
#     photos = await repository_photos.get_photos(skip, limit, db)
#     return templates.TemplateResponse(
#         "photo_list.html", {"request": request, "photos": photos}
#     )


@router.post(
    "/make_QR/",
    status_code=status.HTTP_200_OK,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def make_URL_QR(
    photo_id: int,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    # Generate a QR code URL for a photo.

    This function generates a QR code URL for the specified photo by its ID.

    :param photo_id: int: The ID of the photo for which to generate a QR code URL.
    :param current_user: User
    :param db: AsyncSession: The database session.
    :return: A dictionary containing the QR code URL.
    :rtype: dict
    """

    data = await repository_photos.get_URL_Qr(photo_id, db)

    return data


@router.get(
    "/{photo_id}",
    status_code=status.HTTP_200_OK,
    response_model=PhotosDb,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_one_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Getting a photo by unique photo id"""

    photo = await repository_photos.get_photo_by_id(photo_id, db)

    if photo:
        return photo
    else:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_BY_ID
        )


@router.get(
    "/{username}",
    status_code=status.HTTP_200_OK,
    response_model=PhotosDb,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_photos_for_current_user(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(10, description="Number of records to retrieve"),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """Getting all photos from a database for current user"""
    photos = await repository_photos.get_photos(skip, limit, current_user, db)

    if photos:
        return photos

        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID)


@router.patch(
    "/{photo_id}",
    status_code=status.HTTP_200_OK,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    response_model=PhotosDb,
)
async def patch_pdate_photo(
    photo_id: int,
    new_photo_description: str,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    # Updating a photo by its id
    updated_photo = await repository_photos.update_photo(
        current_user, photo_id, new_photo_description, db
    )

    if updated_photo:
        return jsonable_encoder(updated_photo)

    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID)


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

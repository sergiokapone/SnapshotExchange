from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from fastapi_limiter.depends import RateLimiter

from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import photos as repository_photos
from src.database.models import User, CropMode, BGColor
from src.schemas import (
    MessageResponseSchema,
)

from src.schemas import PhotosDb
from src.services.auth import auth_service
from src.conf.messages import (
    NOT_FOUND,
    PHOTO_REMOVED,
    NO_PHOTO_BY_ID,
    LONG_DESCRIPTION,
)

from src.services.roles import Admin_Moder_User

router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests per minute",
    dependencies=[
        Depends(RateLimiter(times=10, seconds=60)),
        Depends(Admin_Moder_User),
    ],
    response_model=PhotosDb,
)
async def upload_photo(
    photo_file: UploadFile = File(
        ...,
        description="Select a photo to upload (file in .jpg, .jpeg, .png format)",
        file_extension=[".jpg", ".jpeg", ".png"],
    ),
    description: str
    | None = Form(None, description="Add a description to your photo (string)"),
    tags: list[str] = Form(
        None, description="Tags to associate with the photo (list of strings)"
    ),
    width: int
    | None = Form(
        None, description="The desired width for the photo transformation (integer)"
    ),
    height: int
    | None = Form(
        None, description="The desired height for the photo transformation (integer)"
    ),
    crop_mode: CropMode = Form(
        None, description="The cropping mode for the photo transformation (string)"
    ),
    rounding: int | None = Form(None, description="Rounding photo corners (in pixels)"),
    background_color: BGColor = Form(
        None, description="The background color for the photo transformation (string)"
    ),
    rotation_angle: int
    | None = Form(None, description="The angle for the photo transformation (integer)"),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> PhotosDb:
    """
    Upload a Photo

    This endpoint allows users to upload a new photo with various customization options.

    :param photo_file: The photo file to upload (required).
    :type photo_file: UploadFile
    :param str | None description: An optional description for the photo (string, max 500 characters).
    :param list[str] tags: Tags to associate with the photo (list of strings, max 5 tags, each tag max 25 characters).
    :param int | None width: The desired width for the photo transformation (integer).
    :param int | None height: The desired height for the photo transformation (integer).
    :param CropMode | None crop_mode: The cropping mode for the photo transformation (string).
    :param int | None rounding: Rounding photo corners (in pixels).
    :param BGColor | None background_color: The background color for the photo transformation (string).
    :param int | None rotation_angle: The angle for the photo transformation (integer).
    :param current_user: The authenticated user making the upload request.
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: The uploaded photo information.
    :rtype: PhotosDb
    :raises HTTPException 400: If the description is too long or if there are too many tags.
    :raises HTTPException 400: If any tag name is too long.
    :raises HTTPException 400: If the cropping mode or background color is invalid.

    **Example Response:**

    An object containing the uploaded photo information.

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

    if crop_mode is not None:
        crop_mode = crop_mode.name
    else:
        crop_mode = None

    if background_color is not None:
        background_color = background_color.name
    else:
        background_color = "transparent"

    # uploading a new photo
    new_photo = await repository_photos.upload_photo(
        current_user,
        photo_file,
        description,
        db,
        width,
        height,
        crop_mode,
        rounding,
        background_color,
        rotation_angle,
        list_tags,
    )

    response = PhotosDb(
        id=new_photo.id,
        url=new_photo.url,
        description=new_photo.description,
        user_id=new_photo.user_id,
        created_at=new_photo.created_at,
        tags=list_tags,
    )
    if new_photo:
        return response


@router.get(
    "/get_all",
    response_model=list[PhotosDb],
)
async def get_all_photos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    Get All Photos

    This endpoint retrieves a list of photos from the database.

    :param int skip: The number of photos to skip (default is 0).
    :param int limit: The maximum number of photos to retrieve (default is 10).
    :param current_user: The authenticated user (Dependency).
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: A list of Photo objects.
    :rtype: list[PhotosDb]
    :raises HTTPException 401: Unauthorized if the user is not authenticated.
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        GET /get_all?skip=0&limit=10 HTTP/1.1
        Host: yourapi.com
        Authorization: Bearer your_access_token

    **Example Response:**

    .. code-block:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

    .. code-block:: json


        [
        {
            "id": 1,
            "title": "Photo 1",
            "url": "https://example.com/photo1.jpg"
        },
        {
            "id": 2,
            "title": "Photo 2",
            "url": "https://example.com/photo2.jpg"
        }
        ]

    This documentation provides information about the /get_all endpoint, its parameters, the expected response, and potential error responses. You can include this in your Sphinx documentation for your API. If you need further details or have any specific requirements, please let me know.

    """

    photos = await repository_photos.get_photos(skip, limit, db)
    return photos


@router.get("/get_my", response_model=list[PhotosDb])
async def get_my_photos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    Get My Photos


    This endpoint retrieves a list of photos that belong to the authenticated user from the database.

    :param int skip: The number of photos to skip (default is 0).
    :param int limit: The maximum number of photos to retrieve (default is 10).
    :param current_user: The authenticated user (Dependency).
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: A list of Photo objects.
    :rtype: list[PhotosDb]
    :raises HTTPException 401: Unauthorized if the user is not authenticated.
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        GET /get_my?skip=0&limit=10 HTTP/1.1
        Host: yourapi.com
        Authorization: Bearer your_access_token

    **Example Response:**

    .. code-block:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

    .. code-block:: json

        [
        {
            "id": 1,
            "title": "My Photo 1",
            "url": "https://example.com/my_photo1.jpg"
        },
        {
            "id": 2,
            "title": "My Photo 2",
            "url": "https://example.com/my_photo2.jpg"
        }
        ]

    """

    photos = await repository_photos.get_my_photos(skip, limit, current_user, db)
    return photos


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
    Make QR Code for Photo URL


    This endpoint generates a QR code for a specific photo URL.

    :param int photo_id: The ID of the photo for which the QR code is generated.
    :param current_user: The authenticated user (Dependency).
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: The generated QR code data.
    :rtype: bytes
    :raises HTTPException 401: Unauthorized if the user is not authenticated.
    :raises HTTPException 429: Too Many Requests if the rate limit is exceeded.
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        POST /make_QR/?photo_id=123 HTTP/1.1
        Host: yourapi.com
        Authorization: Bearer your_access_token

    **Example Response:**

    The response contains the generated QR code data, which can be used to display or download the QR code image.

    .. code-block:: http

        HTTP/1.1 200 OK
        Content-Type: application/octet-stream

        [QR code binary data]

    **Rate Limiting:**

    This endpoint is rate-limited to no more than 10 requests per minute.

    """

    data = await repository_photos.get_URL_QR(photo_id, db)

    return data


@router.get(
    "/{photo_id}",
    name="get_photo",
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
    """
    Get One Photo by ID

    This endpoint retrieves a specific photo by its unique ID.

    :param int photo_id: The ID of the photo to retrieve.
    :param current_user: The authenticated user (Dependency).
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: The Photo object with the specified ID.
    :rtype: PhotosDb
    :raises HTTPException 204: No Content if no photo with the given ID is found.
    :raises HTTPException 401: Unauthorized if the user is not authenticated.
    :raises HTTPException 429: Too Many Requests if the rate limit is exceeded.
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        GET /123 HTTP/1.1
        Host: yourapi.com
        Authorization: Bearer your_access_token

    **Example Response:**

    The response contains the Photo object with the specified ID.

    .. code-block:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

    .. code-block:: json


        {
            "id": 123,
            "title": "Photo 123",
            "url": "https://example.com/photo123.jpg"
        }

    **Rate Limiting:**

    This endpoint is rate-limited to no more than 10 requests per minute.

    """

    photo = await repository_photos.get_photo_by_id(photo_id, db)

    if photo:
        return photo
    else:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_BY_ID
        )


@router.patch(
    "/{photo_id}",
    name="patch_photo",
    status_code=status.HTTP_200_OK,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    response_model=PhotosDb,
)
async def patch_update_photo(
    photo_id: int,
    new_photo_description: str,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update Photo Description

    This endpoint updates the description of a specific photo by its unique ID.

    :param int photo_id: The ID of the photo to update.
    :param str new_photo_description: The new description for the photo.
    :param current_user: The authenticated user (Dependency).
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: The updated Photo object with the specified ID.
    :rtype: PhotosDb
    :raises HTTPException 404: Not Found if no photo with the given ID is found.
    :raises HTTPException 401: Unauthorized if the user is not authenticated.
    :raises HTTPException 429: Too Many Requests if the rate limit is exceeded.
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        PATCH /123 HTTP/1.1
        Host: yourapi.com
        Authorization: Bearer your_access_token
        Content-Type: application/json

        {
            "new_photo_description": "Updated description for photo 123"
        }

    **Example Response:**

    The response contains the updated Photo object with the specified ID.

    .. code-block:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

    .. code-block:: json

        {
            "id": 123,
            "title": "Photo 123",
            "url": "https://example.com/photo123.jpg",
            "description": "Updated description for photo 123"
        }

    **Rate Limiting:**

    This endpoint is rate-limited to no more than 10 requests per minute.


    """

    # Updating a photo by its id
    updated_photo = await repository_photos.update_photo(
        current_user, photo_id, new_photo_description, db
    )

    if updated_photo:
        return updated_photo

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID)


@router.delete("/{photo_id}", response_model=MessageResponseSchema, name="delete_photo")
async def remove_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseSchema:
    """

    Remove Photo by ID

    This endpoint removes a specific photo by its unique ID.

    :param int photo_id: The ID of the photo to remove.
    :param current_user: The authenticated user (Dependency).
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: A message response indicating the success of the removal.
    :rtype: MessageResponseSchema
    :raises HTTPException 404: Not Found if no photo with the given ID is found.
    :raises HTTPException 401: Unauthorized if the user is not authenticated.
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        DELETE /123 HTTP/1.1
        Host: yourapi.com
        Authorization: Bearer your_access_token

    **Example Response:**

    The response contains a message indicating that the photo has been successfully removed.

    .. code-block:: http

        HTTP/1.1 200 OK
        Content-Type: application/json

    .. code-block:: json

        {
            "message": "Photo removed successfully"
        }

    """

    result = await repository_photos.remove_photo(photo_id, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return {"message": PHOTO_REMOVED}

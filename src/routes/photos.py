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
    Request
)

from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

templates = Jinja2Templates(directory="templates")

from fastapi_limiter.depends import RateLimiter

from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import photos as repository_photos
from src.repository import users as repository_users
from src.repository import ratings as repository_rating
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
    photo_file: UploadFile = File(..., file_extension=[".jpg", ".jpeg", ".png"]),
    description: str | None = Form(None),
    tags: list[str] = Form(None),
    width: int = None,
    height: int = None,
    crop_mode: str = None,
    gravity_mode: str = None,
    rotation_angle: int = None,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseSchema:
    """
    
    Upload a new photo
    -------------------

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
)
async def get_all_photos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
   Get All Photos
   ------------------

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

   .. code-block:: json

      HTTP/1.1 200 OK
      Content-Type: application/json

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

@router.get(
    "/get_my",
    response_model=list[PhotosDb]
)
async def get_all_photos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> list:
    """
   Get My Photos
   ------------------

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

   .. code-block:: json

      HTTP/1.1 200 OK
      Content-Type: application/json

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

@router.get("/get_all/view",
    name="get_all_pages")
async def get_all_photos(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    
    View All Photos
    ------------------

    This endpoint retrieves and displays a view of all photos from the database.

    :param request: The HTTP request object.
    :type request: Request
    :param int skip: The number of photos to skip (default is 0).
    :param int limit: The maximum number of photos to retrieve (default is 10).
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: A rendered HTML page displaying photos with additional information.
    :rtype: templates.TemplateResponse
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        GET /get_all/view?skip=0&limit=10 HTTP/1.1
        Host: yourapi.com

    **Example Response:**

    A rendered HTML page displaying a list of photos with usernames, descriptions, comments, tags, and creation timestamps.


    
    """
    photos = await repository_photos.get_photos(skip, limit, db)
    
    photos_with_username = []
    for photo in photos:
        user = await repository_users.get_user_by_user_id(photo.user_id, db)
        tags = await repository_photos.get_photo_tags(photo.id, db)
        comments = await repository_photos.get_photo_comments(photo.id, db)
        username = user.username if user else None
        rating = await repository_rating.get_rating(photo.id, db)
        formatted_created_at = photo.created_at.strftime("%Y-%m-%d %H:%M:%S")
        qr_code = await repository_photos.get_URL_Qr(photo.id, db)
        
        photos_with_username.append(
            {"id": photo.id, 
             "url": photo.url, 
             "QR": qr_code.get('qr_code_url'),
             "description": photo.description, 
             "username": username, 
             "created_at": formatted_created_at,
             "comments": comments,
             "tags": tags,
             "rating": rating
             },
            )

    return templates.TemplateResponse(
        "photo_list.html", {"request": request, "photos": photos_with_username}
    )


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
    --------------------------

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

    .. code-block:: binary

        HTTP/1.1 200 OK
        Content-Type: application/octet-stream

        [QR code binary data]

    **Rate Limiting:**

    This endpoint is rate-limited to no more than 10 requests per minute.

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
    """
    Get One Photo by ID
    --------------------

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

    .. code-block:: json

        HTTP/1.1 200 OK
        Content-Type: application/json

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
    """
    Update Photo Description
    ------------------------

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

    .. code-block:: json

        HTTP/1.1 200 OK
        Content-Type: application/json

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
        return jsonable_encoder(updated_photo)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_PHOTO_BY_ID)


@router.delete("/{photo_id}", response_model=MessageResponseSchema)
async def remove_photo(
    photo_id: int,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponseSchema:
    """
    
    Remove Photo by ID
    ------------------

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

    .. code-block:: json

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "message": "Photo removed successfully"
    }

    """

    result = await repository_photos.remove_photo(photo_id, current_user, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return {"message": PHOTO_REMOVED}

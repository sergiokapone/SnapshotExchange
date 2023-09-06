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


@router.get("/view_all_photos", include_in_schema=False, name="view_all_photos")
async def view_all_photos(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """

    View All Photos

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
        qr_code = await repository_photos.get_URL_QR(photo.id, db)

        photos_with_username.append(
            {
                "id": photo.id,
                "url": photo.url,
                "QR": qr_code.get("qr_code_url"),
                "description": photo.description,
                "username": username,
                "created_at": formatted_created_at,
                "comments": comments,
                "tags": tags,
                "rating": rating,
            },
        )

    return templates.TemplateResponse(
        "photo_list.html", {"request": request, "photos": photos_with_username}
    )

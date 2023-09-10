from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query, Request, Cookie

from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse


from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect_db import get_db
from src.repository import photos as repository_photos
from src.repository import search as repository_search


templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["Views"])


@router.get("/database", include_in_schema=False, name="view_all_photos")
async def view_database(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    access_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    """
    View All Photos

    This endpoint retrieves and displays a view of all photos from the database.

    :param request: The HTTP request object.
    :type request: Request
    :param skip: The number of photos to skip (default is 0).
    :param limit: The maximum number of photos to retrieve (default is 10).
    :param current_user: The authenticated user (Dependency).
    :type current_user: User
    :param db: The asynchronous database session (Dependency).
    :type db: AsyncSession
    :return: A rendered HTML page displaying photos with additional information.
    :rtype: templates.TemplateResponse
    :raises HTTPException 500: Internal Server Error if there's a database issue.

    **Example Request:**

    .. code-block:: http

        GET /view_all_photos?skip=0&limit=10 HTTP/1.1
        Host: yourapi.com

    **Example Response:**

    A rendered HTML page displaying a list of photos with usernames, descriptions, comments, tags, and creation timestamps.
    """

    if not access_token:
        return RedirectResponse(url=request.url_for("login_page"))

    photos = await repository_photos.get_photos(skip, limit, db)

    detailed_info = []

    for photo in photos:
        info = await repository_photos.get_photo_info(photo, db)
        detailed_info.append(info)

    context = {
        "request": request,
        "photos": detailed_info,
        "skip": skip,
        "limit": limit,
        "access_token": access_token,
    }

    return templates.TemplateResponse("database.html", context)


@router.get("/search", name="search_by_tag")
async def search_by_tag(
    request: Request,
    query: str,
    search_type: str,
    # skip: int = 0,
    # limit: int = 10,
    access_token: str = Cookie(None),
    rating_low: float = Query(0),
    rating_high: float = Query(999),
    start_data: str = Query(datetime.now().date() - timedelta(days=365 * 60)),
    end_data: str = Query(datetime.now().date()),
    db: AsyncSession = Depends(get_db),
):
    start_date = datetime.strptime(str(start_data), "%Y-%m-%d").date()
    end_date = datetime.strptime(str(end_data), "%Y-%m-%d").date()

    if search_type == "tag":
        photos = await repository_search.search_by_tag(
            query, rating_low, rating_high, start_date, end_date, db
        )
    elif search_type == "description":
        photos = await repository_search.search_by_description(
            query, rating_low, rating_high, start_date, end_date, db
        )
    elif search_type == "username":
        photos = await repository_search.search_by_username(query, db)
    else:
        # Обработка неверного значения search_type, например, бросить ошибку
        return JSONResponse(content={"error": "Invalid search_type"}, status_code=400)

    if not access_token:
        return RedirectResponse(url=request.url_for("login_page"))

    detailed_info = []

    for photo in photos:
        info = await repository_photos.get_photo_info(photo, db)
        detailed_info.append(info)

    context = {
        "request": request,
        "photos": detailed_info,
        "skip": 0,
        "limit": len(photos) + 1,
        "access_token": access_token,
    }

    return templates.TemplateResponse("database.html", context)

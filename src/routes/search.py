from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import BAD_DATE_FORMAT
from src.database.connect_db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.repository.search import search_admin, search_by_description, search_by_tag
from src.services.roles import Admin_Moder

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/tag/{tag}", tags=["Search"])
async def search_tag(
    tag: str = Path(min_length=2),
    rating_low: float = Query(0),
    rating_high: float = Query(999),
    start_data: str = Query(datetime.now().date() - timedelta(days=365 * 60)),
    end_data: str = Query(datetime.now().date()),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search photos with "tag" optional filtering by "rating", and "date range".

    This function allows users to search for photos based on a provided "tag". Users can also filter search
    results by specifying minimum and maximum "rating values", as well as a "date range".
    Parameter "tag" must be a string minimum 2 characters.
    Parameter "rating" is float number.
    Parameter "date range" is a string in the format "YYYY-MM-DD"
    The search is performed within the specified parameters.

    :param tag: str: The search text or tag to filter photos.

    :param rating_low: float: The minimum rating value to filter photos.

    :param rating_high: float: The maximum rating value to filter photos.

    :param start_data: str: The start date for the search range in 'YYYY-MM-DD' format.

    :param end_data: str: The end date for the search range in 'YYYY-MM-DD' format.

    :param current_user: User: The currently authenticated user.

    :param db: AsyncSession: The database session.

    :return: A list of photos that match the search criteria.

    :rtype: List[Photo]
    """
    try:
        start_date = datetime.strptime(start_data, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_data, "%Y-%m-%d").date()
        photos = await search_by_tag(
            tag, rating_low, rating_high, start_date, end_date, db
        )
        return {"photos": photos}
    except ValueError as e:
        return {"details": BAD_DATE_FORMAT}


@router.get("/description/{description}", tags=["Search"])
async def search_description(
    description: str = Path(min_length=2),
    rating_low: float = Query(0),
    rating_high: float = Query(999),
    start_data: str = Query(datetime.now().date() - timedelta(days=365 * 60)),
    end_data: str = Query(datetime.now().date()),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search photos with matching in "description" and optional filtering by "rating", and "date range".

    This function allows users to search for photos based on a provided text. Users can also filter search
    results by specifying minimum and maximum "rating values", as well as a "date range".
    Parameter "text" must be a string minimum 2 characters.
    Parameter "rating" is float number.
    Parameter "date range" is a string in the format "YYYY-MM-DD"
    The search is performed within the specified parameters.

    :param description: str: The search text or tag to filter photos.
    :param rating_low: float: The minimum rating value to filter photos.
    :param rating_high: float: The maximum rating value to filter photos.
    :param start_data: str: The start date for the search range in 'YYYY-MM-DD' format.
    :param end_data: str: The end date for the search range in 'YYYY-MM-DD' format.
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: A list of photos that match the search criteria.
    :rtype: List[Photo]
    """
    try:
        start_date = datetime.strptime(start_data, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_data, "%Y-%m-%d").date()
        photos = await search_by_description(
            description, rating_low, rating_high, start_date, end_date, db
        )
        return {"photos": photos}
    except ValueError as e:
        return {"details": BAD_DATE_FORMAT}


@router.get(
    "/admin_search/{user_id}", dependencies=[Depends(Admin_Moder)], tags=["Search"]
)
async def admin_search(
    user_id: int,
    text: str = Query(None, min_length=2),
    rating_low: float = Query(0),
    rating_high: float = Query(999),
    start_data: str = Query(str(datetime.now().date() - timedelta(days=365 * 60))),
    end_data: str = Query(str(datetime.now().date())),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search photos for administrators by "user_id" with optional filtering by "tag" or "description",
    "rating", and "date range".

    This function allows administrators to search for photos based on a provided "user_id" and filter search results
    by matching "text" with "tags"(if text start with "#") or matching with "descriptions",
    minimum and maximum "rating values", as well as a "date range".
    Parameter "text" must be a string minimum 2 characters.
    Parameter "rating" is float number.
    Parameter "date range" is a string in the format "YYYY-MM-DD"
    The search is performed within the "user_id" parameter and optional "text", "rating range" and "date range"

    :param text: str: The search text or tag to filter photos.
    :param user_id: int: The user ID to filter photos. Leave as None to search all users' photos.

    :param rating_low: float: The minimum rating value to filter photos.

    :param rating_high: float: The maximum rating value to filter photos.

    :param start_data: str: The start date for the search range in 'YYYY-MM-DD' format.

    :param end_data: str: The end date for the search range in 'YYYY-MM-DD' format.

    :param current_user: User: The currently authenticated user (administrator).

    :param db: AsyncSession: The database session.

    :return: A list of photos that match the search criteria.

    :rtype: List[Photo]
    """
    try:
        start_date = datetime.strptime(start_data, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_data, "%Y-%m-%d").date()
        photos = await search_admin(
            user_id, text, rating_low, rating_high, start_date, end_date, db
        )
        return {"photos": photos}
    except ValueError as e:
        return {"details": BAD_DATE_FORMAT}

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import BAD_DATE_FORMAT
from src.database.connect_db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.repository.search import search, search_admin
from src.services.roles import Admin_Moder

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/{tag}", tags=["Search"])
async def search_photo(tag: str = Path(min_length=2), rating_low: float = Query(0),
                       rating_high: float = Query(999),
                       start_data: str = Query(str(datetime.now().date() - timedelta(days=365 * 60))),
                       end_data: str = Query(str(datetime.now().date())),
                       current_user: User = Depends(auth_service.get_authenticated_user),
                       db: AsyncSession = Depends(get_db)):
    """
    Search photos with optional filtering by tag, rating, and date range.

    This function allows users to search for photos based on a provided tag. Users can also filter search results by specifying
    minimum and maximum rating values, as well as a date range. The search is performed within the specified parameters.

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
        start_date = datetime.strptime(start_data, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_data, '%Y-%m-%d').date()
        photos = await search(tag, rating_low, rating_high, start_date, end_date, db)
        return {"photos": photos}
    except ValueError as e:
        return {"details": BAD_DATE_FORMAT}


@router.get("/admin_search/{tag}", dependencies=[Depends(Admin_Moder)], tags=["Search"])
async def admin_search(tag: str = Path(min_length=2), user_id: int = Query(None), rating_low: float = Query(0),
                       rating_high: float = Query(999),
                       start_data: str = Query(str(datetime.now().date() - timedelta(days=365 * 60))),
                       end_data: str = Query(str(datetime.now().date())),
                       current_user: User = Depends(auth_service.get_authenticated_user),
                       db: AsyncSession = Depends(get_db)):
    """
    Search photos for administrators with optional filtering by tag, user, rating, and date range.

    This function allows administrators to search for photos based on a provided tag and filter search results by specifying
    user, minimum and maximum rating values, as well as a date range. The search is performed within the specified parameters.

    :param tag: str: The search text or tag to filter photos.
    
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
        start_date = datetime.strptime(start_data, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_data, '%Y-%m-%d').date()
        photos = await search_admin(tag, user_id, rating_low, rating_high, start_date, end_date, db)
        return {"photos": photos}
    except ValueError as e:
        return {"details": BAD_DATE_FORMAT}

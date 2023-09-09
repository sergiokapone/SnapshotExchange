from datetime import datetime, date, timedelta

from sqlalchemy import select, and_, cast, Date, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.database.models import (
    User,
    Role,
    BlacklistToken,
    Post,
    Rating,
    Photo,
    Comment,
    Tag,
)


async def search_by_tag(
    tag: str,
    rating_low: float,
    rating_high: float,
    start_data: date,
    end_data: date,
    db: AsyncSession,
) -> [Photo]:
    """
    Search photos by match in tags, with optional filtering by rating and date range.

    :param tag: Search text
    :type tag: str
    :param rating_low: Minimum rating
    :type rating_low: float
    :param rating_high: Maximum rating
    :type rating_high: float
    :param start_data: Start date for the search range.
    :type start_data: Date
    :param end_data: End date for the search range.
    :type end_data: Date
    :param db: The database session
    :type db: AsyncSession
    :return: List of photos
    :rtype: List[Photo]
    """
    query = select(Photo).join(Tag, Photo.tags).filter(Tag.name.ilike(f"%{tag}%"))
    if rating_low > 0 or rating_high < 999:
        query = query.filter(
            Photo.ratings.has(
                and_(Rating.rating >= rating_low, Rating.rating <= rating_high)
            )
        )
    if (
        start_data != datetime.now().date() - timedelta(days=365 * 60)
        or end_data != datetime.now().date()
    ):
        query = query.filter(
            cast(Photo.created_at, Date) >= start_data,
            cast(Photo.created_at, Date) <= end_data,
        )
    photos_with_tag = await db.execute(query)
    photos = photos_with_tag.scalars().all()
    return photos


async def search_by_description(
    text: str,
    rating_low: float,
    rating_high: float,
    start_data: date,
    end_data: date,
    db: AsyncSession,
) -> [Photo]:
    """
    Search photos by match in description, with optional filtering by rating and date range.

    :param text: Search text
    :type text: str
    :param rating_low: Minimum rating
    :type rating_low: float
    :param rating_high: Maximum rating
    :type rating_high: float
    :param start_data: Start date for the search range.
    :type start_data: Date
    :param end_data: End date for the search range.
    :type end_data: Date
    :param db: The database session
    :type db: AsyncSession
    :return: List of photos
    :rtype: List[Photo]
    """
    query = select(Photo).filter(Photo.description.ilike(f"%{text}%"))
    if rating_low > 0 or rating_high < 999:
        query = query.filter(
            Photo.ratings.has(
                and_(Rating.rating >= rating_low, Rating.rating <= rating_high)
            )
        )
    if (
        start_data != (datetime.now().date() - timedelta(days=365 * 60))
        or end_data != datetime.now().date()
    ):
        query = query.filter(
            cast(Photo.created_at, Date) >= start_data,
            cast(Photo.created_at, Date) <= end_data,
        )

    photos_by_description = await db.execute(query)
    photos = photos_by_description.scalars().all()
    return photos


async def search_admin(
    user_id: int,
    text: str,
    rating_low: float,
    rating_high: float,
    start_data: date,
    end_data: date,
    db: AsyncSession,
) -> [Photo]:
    """
    Search photos for admin by user with optional filtering by tag, rating and date range.

    :param text: Search text
    :type text: str
    :param user_id: user id for search
    :type user_id: int
    :param rating_low: Minimum rating
    :type rating_low: float
    :param rating_high: Maximum rating
    :type rating_high: float
    :param start_data: Start date for the search range.
    :type start_data: Date
    :param end_data: End date for the search range.
    :type end_data: Date
    :param db: The database session
    :type db: AsyncSession
    :return: List of photos
    :rtype: List[Photo]
    """
    query = select(Photo).filter_by(user_id=user_id)
    if text:
        if text.startswith("#"):
            query = query.join(Tag, Photo.tags).filter(
                Tag.name.ilike(f"%{text.removeprefix('#')}%")
            )
        else:
            query = query.filter(Photo.description.ilike(f"%{text}%"))

    if rating_low > 0 or rating_high < 999:
        query = query.filter(
            Photo.ratings.has(
                and_(Rating.rating >= rating_low, Rating.rating <= rating_high)
            )
        )
    if (
        start_data != (datetime.now().date() - timedelta(days=365 * 60))
        or end_data != datetime.now().date()
    ):
        query = query.filter(
            cast(Photo.created_at, Date) >= start_data,
            cast(Photo.created_at, Date) <= end_data,
        )

    photos_by_user = await db.execute(query)
    photos = photos_by_user.scalars().all()
    return photos

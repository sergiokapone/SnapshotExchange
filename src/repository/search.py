from datetime import datetime, date

from sqlalchemy import select, and_, cast, Date, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.database.models import User, Role, BlacklistToken, Post, Rating, Photo, Comment, Tag


async def search_by_tag(tag: str, rating_low: float, rating_high: float, start_data: date, end_data: date,
                        db: AsyncSession) -> [Photo]:
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
    query = select(Photo).join(Photo.tags).filter(
        and_(
            func.DATE(Photo.created_at) >= start_data,
            func.DATE(Photo.created_at) <= end_data,
            Tag.name.ilike(f'%{tag}%')
        )
    )

    if rating_low > 0 and rating_high < 999:
        query = query.filter(
            and_(
                Photo.ratings.has(and_(
                    Rating.rating >= rating_low,
                    Rating.rating <= rating_high
                )),
                func.DATE(Photo.created_at) >= start_data,
                func.DATE(Photo.created_at) <= end_data,
                Tag.name.ilike(f'%{tag}%')
            )
        )

    photos = await db.execute(query)
    result = photos.scalars().all()
    return result


async def search_by_description(text: str, rating_low: float, rating_high: float, start_data: date, end_data: date,
                                db: AsyncSession) -> [Photo]:
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

    if rating_low == 0 and rating_high == 999:
        photos_by_description = await db.execute(
            select(Photo)
            .filter(Photo.description.ilike(f"%{text}%"))
            .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
        )
        photos = photos_by_description.scalars().all()
        return photos

    photos_by_description = await db.execute(
        select(Photo).filter(Photo.description.ilike(f"%{text}%"))
        .filter(Photo.ratings.has(and_(Rating.rating >= rating_low, Rating.rating <= rating_high)))
        .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
    )
    photos = photos_by_description.scalars().all()
    if photos:
        return photos
    return []


async def search_admin(user_id: int, tag: str, rating_low: float, rating_high: float, start_data: date, end_data: date,
                       db: AsyncSession) -> [Photo]:
    """
    Search photos for admin by user, tag, with optional filtering by rating and date range.

    :param tag: Search text
    :type tag: str
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
    existing_tags = await db.execute(select(Tag).filter(Tag.name.ilike(f"%{tag}%")))
    matching_tags_instances = existing_tags.scalars().all()


    if rating_low == 0 and rating_high == 999:
        photos_with_tag = await db.execute(
            select(Photo)
            .filter(Photo.user_id == user_id)
            .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
            .join(Tag.photos)
            .filter(Tag.in_(matching_tags_instances))
            )
        photos = photos_with_tag.scalars().all()
        return photos
    photos_with_tag = await db.execute(
        select(Photo)
        .filter(Photo.user_id == user_id)
        .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
        .join(Tag.photos)
        .filter(Tag.in_(matching_tags_instances))
        .filter(Photo.ratings.has(and_(Rating.rating >= rating_low, Rating.rating <= rating_high)))

    )
    photos = photos_with_tag.scalars().all()
    return photos

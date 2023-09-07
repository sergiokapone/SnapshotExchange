from datetime import datetime, date

from sqlalchemy import select, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models import User, Role, BlacklistToken, Post, Rating, Photo, Comment, Tag


async def search(tag: str, rating_low: float, rating_high: float, start_data: date, end_data: date, db: AsyncSession
                 ) -> [Photo]:
    """
    Search photos by tag, with optional filtering by rating and date range.

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
    existing_tag = await db.execute(select(Tag).filter(Tag.name == tag))
    tag_instance = existing_tag.scalar()

    if tag_instance:
        if rating_low == 0 and rating_high == 999:
            photos_with_tag = await db.execute(
                select(Photo)
                .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
                .join(Tag.photos)
                .filter(Tag.id == tag_instance.id)
                )
            photos = photos_with_tag.scalars().all()
            return photos
        photos_with_tag = await db.execute(
            select(Photo)
            .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
            .join(Tag.photos)
            .filter(Tag.id == tag_instance.id)
            .filter(Photo.ratings.has(and_(Rating.rating >= rating_low, Rating.rating <= rating_high)))

        )
        photos = photos_with_tag.scalars().all()
        return photos

    elif rating_low == 0 and rating_high == 999:
        photos_by_description = await db.execute(
            select(Photo)
            .filter(Photo.description.ilike(f"%{tag}%"))
            .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
        )
        photos = photos_by_description.scalars().all()
        return photos

    photos_by_description = await db.execute(
        select(Photo).filter(Photo.description.ilike(f"%{tag}%"))
        .filter(Photo.ratings.has(and_(Rating.rating >= rating_low, Rating.rating <= rating_high)))
        .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
    )
    photos = photos_by_description.scalars().all()
    if photos:
        return photos
    return []


async def search_admin(tag: str, user_id: int, rating_low: float, rating_high: float, start_data: date, end_data: date,
                       db: AsyncSession) -> [Photo]:
    """
    Search photos for admin by tag, user, with optional filtering by rating and date range.

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
    existing_tag = await db.execute(select(Tag).filter(Tag.name == tag))
    tag_instance = existing_tag.scalar()

    if tag_instance:
        if rating_low == 0 and rating_high == 999:
            photos_with_tag = await db.execute(
                select(Photo)
                .filter(Photo.user_id == user_id)
                .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
                .join(Tag.photos)
                .filter(Tag.id == tag_instance.id)
                )
            photos = photos_with_tag.scalars().all()
            return photos
        photos_with_tag = await db.execute(
            select(Photo)
            .filter(Photo.user_id == user_id)
            .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
            .join(Tag.photos)
            .filter(Tag.id == tag_instance.id)
            .filter(Photo.ratings.has(and_(Rating.rating >= rating_low, Rating.rating <= rating_high)))

        )
        photos = photos_with_tag.scalars().all()
        return photos

    elif rating_low == 0 and rating_high == 999:
        photos_by_description = await db.execute(
            select(Photo)
            .filter(Photo.user_id == user_id)
            .filter(Photo.description.ilike(f"%{tag}%"))
            .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
        )
        photos = photos_by_description.scalars().all()
        return photos

    photos_by_description = await db.execute(
        select(Photo)
        .filter(Photo.user_id == user_id)
        .filter(Photo.description.ilike(f"%{tag}%"))
        .filter(Photo.ratings.has(and_(Rating.rating >= rating_low, Rating.rating <= rating_high)))
        .filter(cast(Photo.created_at, Date) >= start_data, cast(Photo.created_at, Date) <= end_data)
    )
    photos = photos_by_description.scalars().all()
    if photos:
        return photos
    return []

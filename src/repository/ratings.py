from datetime import datetime
import math
from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from fastapi import HTTPException, status
from src.conf.config import init_cloudinary
from src.conf.messages import YOUR_PHOTO, ALREADY_LIKE
from src.database.models import User, Role, BlacklistToken, Post, Rating, Photo
from src.schemas import UserSchema, UserProfileSchema


async def create_rating(rating: int, photos_id: int, user: User, db: AsyncSession):
    """
    Create a new rating for a photo in the database.

    :param rating: The rating value.
    :type rating: str
    :param photos_id: The ID of the photo to rate.
    :type photos_id: str
    :param user: The user who is creating the rating.
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The created rating object.
    :rtype: Rating
    """
    query = select(Photo).filter(Photo.id == photos_id)  # Получить информацию о фотографии по её ID
    photo = await db.execute(query)
    photo = photo.scalar()

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=PHOTO_NOT_FOUND
        )

    if photo.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=YOUR_PHOTO
        )

    query = select(Rating).filter(
        Rating.user_id == user.id,
        Rating.photo_id == photos_id,
    )
    result = await db.execute(query)
    exsist_photo = result.scalars().all()
    if exsist_photo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ALREADY_LIKE
        )

    new_rating = Rating(rating=rating, user_id=user.id, photo_id=photos_id)
    try:
        db.add(new_rating)
        await db.commit()
        await db.refresh(new_rating)
    except Exception as e:
        raise e


    return new_rating


async def get_rating(photos_id: int, db: AsyncSession):
    """
    Calculate and retrieve the average rating for a photo.

    :param photos_id: The ID of the photo for which to calculate the rating.
    :type photos_id: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The average rating for the photo.
    :rtype: float
    """
    query = select(Rating).filter(Rating.photo_id == photos_id)

    result = await db.execute(query)
    all_ratings = result.scalars().all()
    count_ratings = len(all_ratings)
    if count_ratings == 0:
        return 0
    res = 0
    for i in all_ratings:
        res += i.rating
    
    average_rating = res / count_ratings
   
    return average_rating


async def get_all_ratings(photos_id: int, db: AsyncSession):
    """
    Retrieve all ratings for a photo.

    :param photos_id: The ID of the photo for which to retrieve ratings.
    :type photos_id: str
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of rating objects.
    :rtype: List[Rating]
    """
    query = select(Rating).filter(Rating.photo_id == photos_id)

    result = await db.execute(query)
    all_ratings = result.scalars().all()

    return all_ratings


async def delete_all_ratings(photos_id: int, user_id: int, db: AsyncSession):
    """
    Delete all ratings by a specific user for a photo.

    :param photos_id: The ID of the photo for which to delete ratings.
    :type photos_id: str
    :param user_id: The ID of the user whose ratings should be deleted.
    :type user_id: str
    :param db: The database session.
    :type db: AsyncSession
    :return: A message indicating whether ratings were deleted.
    :rtype: dict
    """
    query = select(Rating).filter(
        Rating.photo_id == photos_id, Rating.user_id == user_id
    )

    result = await db.execute(query)
    rating_to_delete = result.scalar()

    if rating_to_delete:
        try:
            await db.delete(rating_to_delete)
            await db.commit()
            return {"message": "Rating delete"}
        except Exception as e:
            raise e

    return {"message": "Rating dont find"}

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import ratings as repository_ratings

from src.database.models import User, Role

from src.schemas import (
    UserProfileSchema,
    UserResponseSchema,
    RequestEmail,
    UserDb,
    RequestRole,
    PhotoRat,
    Rating,
)


from src.services.auth import auth_service

from src.services.roles import RoleChecker

from src.conf.messages import (
    NOT_FOUND,
    USER_ROLE_EXISTS,
    INVALID_EMAIL,
    USER_NOT_ACTIVE,
    USER_ALREADY_NOT_ACTIVE,
    USER_CHANGE_ROLE_TO,
    FORBIDDEN,
    DELETE_SUCCESSFUL,
)


router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/created_rating/", response_model=Rating)
async def created_rating(rating:int,photo_id:int,current_user: User = Depends(auth_service.get_authenticated_user), db: AsyncSession = Depends(get_db)):
    """
    Create a new rating for a photo.

    This function allows users to create a new rating for a photo. Users must be authenticated.
    The function accepts the rating value, the ID of the photo being rated, the current authenticated user, and a database session.

    :param rating: int: The rating value.
    :param photo_id: int: The ID of the photo being rated.
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: The newly created rating record.
    :rtype: Rating
    """
    new_rating=await repository_ratings.create_rating(rating,photo_id,current_user,db)

    return new_rating


@router.get("/get_rating/")
async def get_rating(photo_id:int, db: AsyncSession = Depends(get_db)):
    """
    Get the average rating for a photo.

    This function retrieves the average rating for a photo with the specified ID from the database.

    :param photo_id: int: The ID of the photo.
    :param db: AsyncSession: The database session.
    :return: The average rating for the photo.
    :rtype: float
    """
    new_rating=await repository_ratings.get_rating(photo_id,db)

    return new_rating

@router.get("/get_rating_admin/")
async def get_rating_ADmin_Moder(photo_id:int,current_user: User = Depends(auth_service.get_authenticated_user), db: AsyncSession = Depends(get_db)):
    """
    Get all ratings for a photo (Admin/Moderator only).

    This function retrieves all ratings for a photo with the specified ID from the database.
    Only users with the 'admin' or 'moder' role can access this endpoint.

    :param photo_id: int: The ID of the photo.
    :param current_user: User: The currently authenticated user (admin or moder).
    :param db: AsyncSession: The database session.
    :return: All ratings for the photo.
    :rtype: List[Rating]
    """
    if current_user.role == Role.user:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=FORBIDDEN
            ) 
    else:
        new_rating=await repository_ratings.get_all_ratings(photo_id,db)
        return new_rating
    

@router.delete("/delete_rating_admin/")
async def delete_rating_ADmin_Moder(photo_id:int,user_id:int,current_user: User = Depends(auth_service.get_authenticated_user), db: AsyncSession = Depends(get_db)):
    """
    Delete all ratings for a photo (Admin/Moderator only).

    This function deletes all ratings for a photo with the specified ID and user ID from the database.
    Only users with the 'admin' or 'moder' role can access this endpoint.

    :param photo_id: int: The ID of the photo.
    :param user_id: int: The ID of the user.
    :param current_user: User: The currently authenticated user (admin or moder).
    :param db: AsyncSession: The database session.
    :return: A message indicating successful deletion.
    :rtype: MessageResponseSchema
    """
    if current_user.role == Role.user:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=FORBIDDEN
            ) 
    else:
        await repository_ratings.delete_all_ratings(photo_id,user_id,db)
        return DELETE_SUCCESSFUL




from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import ratings as repository_ratings

from src.database.models import User, Role

from src.schemas import (
    UserProfile,
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

# Permissions to use routes by role

allowed_get_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_create_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_get_all_users = RoleChecker([Role.admin])
allowed_remove_user = RoleChecker([Role.admin])
allowed_ban_user = RoleChecker([Role.admin])
allowed_change_user_role = RoleChecker([Role.admin])


@router.post("/created_photo/", response_model=PhotoRat)
async def create_photo_(content:str, current_user: User = Depends(auth_service.get_authenticated_user), db: AsyncSession = Depends(get_db)):
    new_photo=await repository_ratings.create_photo(content,current_user,db)

    return new_photo


@router.post("/created_rating/", response_model=Rating)
async def created_rating(rating,photo_id,current_user: User = Depends(auth_service.get_authenticated_user), db: AsyncSession = Depends(get_db)):
    new_rating=await repository_ratings.create_rating(rating,photo_id,current_user,db)

    return new_rating


@router.get("/get_rating/")
async def get_rating(photo_id, db: AsyncSession = Depends(get_db)):
    new_rating=await repository_ratings.get_rating(photo_id,db)

    return new_rating

@router.get("/get_rating_admin/")
async def get_rating_ADmin_Moder(photo_id,current_user: User = Depends(auth_service.get_authenticated_user), db: AsyncSession = Depends(get_db)):
    if current_user.role == Role.user:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=FORBIDDEN
            ) 
    else:
        new_rating=await repository_ratings.get_all_ratings(photo_id,db)
        return new_rating
    

@router.delete("/delete_rating_admin/")
async def delete_rating_ADmin_Moder(photo_id,user_id,current_user: User = Depends(auth_service.get_authenticated_user), db: AsyncSession = Depends(get_db)):
    if current_user.role == Role.user:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=FORBIDDEN
            ) 
    else:
        await repository_ratings.delete_all_ratings(photo_id,user_id,db)
        return DELETE_SUCCESSFUL




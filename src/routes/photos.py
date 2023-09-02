from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form, Query
from fastapi_limiter.depends import RateLimiter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import PHOTO_UPLOADED, NO_PHOTO_FOUND
from src.database.connect_db import get_db
from src.database.models import User
from src.repository import photos as repository_photos
from src.services.auth import auth_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{username}",
            status_code=status.HTTP_200_OK,
            response_model=dict,
            description="No more than 10 requests per minute",
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def get_all_photos(skip: int = Query(0, description="Number of records to skip"),
                         limit: int = Query(10, description="Number of records to retrieve"),
                         current_user: User = Depends(auth_service.get_authenticated_user),
                         db: AsyncSession = Depends(get_db)):
    """Getting all photos from a database for current user"""
    photos_dict = await repository_photos.get_all_photos(skip, limit, current_user, db)

    if photos_dict:
        return jsonable_encoder(photos_dict)
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_FOUND)


@router.get("/{username}/{photo_id}",
            status_code=status.HTTP_200_OK,
            response_model=dict,
            description="No more than 10 requests per minute",
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def get_one_photo(photo_id: str,
                        current_user: User = Depends(auth_service.get_authenticated_user),
                        db: AsyncSession = Depends(get_db)):
    """Getting a photo for current user by unique photo id"""

    photo = await repository_photos.get_photo_by_id(current_user, photo_id, db)

    if photo:
        return jsonable_encoder(photo)
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=NO_PHOTO_FOUND)


@router.post("/{username}", status_code=status.HTTP_201_CREATED,
             description="No more than 10 requests per minute",
             dependencies=[Depends(RateLimiter(times=10, seconds=60))]
             )
async def upload_new_photo(photo_file: UploadFile = File(),
                           description: str = Form(None),
                           current_user: User = Depends(auth_service.get_authenticated_user),
                           db: AsyncSession = Depends(get_db)):
    """Upload new photos"""
    if description is not None:
        if len(description) > 500:
            raise HTTPException(status_code=400, detail="Description is too long. Maximum length is 500 characters.")
        new_photo = await repository_photos.upload_photo(current_user, photo_file, db, description)
    else:
        new_photo = await repository_photos.upload_photo(current_user, photo_file, db)

    if new_photo:
        return HTTPException(status_code=status.HTTP_201_CREATED, detail=PHOTO_UPLOADED)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

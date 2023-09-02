import time
import random

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException, status, BackgroundTasks, Form
from fastapi.templating import Jinja2Templates
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connect_db import get_db
from src.database.models import Photo, Tag, User
from src.repository import photos as repository_photos
from src.schemas import UserResponseSchema
from src.services.auth import auth_service

router = APIRouter(prefix="/photos", tags=["photos"])

load_dotenv()


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
        return f"New photo successfully uploaded"
    return status.HTTP_501_NOT_IMPLEMENTED

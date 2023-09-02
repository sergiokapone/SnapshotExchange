import time
import random
from typing import Type

import cloudinary
import cloudinary.uploader

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from src.conf.config import init_cloudinary
from src.database.connect_db import get_db
from src.repository import ratings as repository_ratings

from src.database.models import User, Photo

init_cloudinary()


async def get_user_by_email(email: str, db: AsyncSession) -> Type[User]:
    q = select(User).where(User.email == email)
    result = await db.execute(q)
    user = result.scalar_one_or_none()
    if user:
        return user


async def upload_photo(current_user: User, photo: File(), db: AsyncSession, description=None) -> bool:
    user = await get_user_by_email(current_user.email, db)
    if user:
        unique_photo_id = f"{int(time.time())}-{random.randint(1, 10_000)}"
        public_photo_id = f"Photos of users/{current_user.username}/{unique_photo_id}"

        uploaded_file_info = cloudinary.uploader.upload(photo.file, public_id=public_photo_id, overwrite=True)

        photo_url = cloudinary.CloudinaryImage(public_photo_id).build_url(width=250, height=250,
                                                                          crop="fill",
                                                                          version=uploaded_file_info.get('version'))
        # add photo url to DB
        new_photo = Photo(url=photo_url,
                          description=description,
                          user_id=user.id)
        db.add(new_photo)
        await db.commit()
        await db.refresh(new_photo)

        return status.HTTP_201_CREATED

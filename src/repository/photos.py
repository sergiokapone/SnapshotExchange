import time
import random

import cloudinary
import cloudinary.uploader

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import File, status

from src.conf.config import init_cloudinary
from src.database.models import User, Photo

init_cloudinary()


async def upload_photo(current_user: User, photo: File(), db: AsyncSession, description=None) -> status:
    unique_photo_id = f"{int(time.time())}-{random.randint(1, 10_000)}"
    public_photo_id = f"Photos of users/{current_user.username}/{unique_photo_id}"

    uploaded_file_info = cloudinary.uploader.upload(photo.file, public_id=public_photo_id, overwrite=True)

    photo_url = cloudinary.CloudinaryImage(public_photo_id).build_url(width=250, height=250,
                                                                      crop="fill",
                                                                      version=uploaded_file_info.get('version'))
    # add photo url to DB
    new_photo = Photo(url=photo_url,
                      description=description,
                      user_id=current_user.id)
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)

    return status.HTTP_201_CREATED


async def get_all_photos(skip: int, limit: int, current_user: User, db: AsyncSession) -> dict:
    db_query = select(Photo).where(Photo.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(db_query)
    photos = result.scalars()

    photo_dict = {photo.url: photo.description for photo in photos}

    if photo_dict:
        return photo_dict


async def get_photo_by_id(current_user: User, photo_id: str, db: AsyncSession) -> dict:
    query_result = await db.execute(select(Photo).where(Photo.user_id == current_user.id))
    photos = query_result.scalars()

    for photo in photos:
        p_id = photo.url.split('/')[-1]
        if photo_id == p_id:
            return {photo.url: photo.description}


async def patch_update_photo(current_user: User, photo_id: str, description: str, db: AsyncSession) -> dict:
    query_result = await db.execute(select(Photo).where(Photo.user_id == current_user.id))
    photos = query_result.scalars()

    for photo in photos:
        p_id = photo.url.split('/')[-1]
        if photo_id == p_id:
            photo.description = description
            await db.commit()
            await db.refresh(photo)

            return {photo.url: photo.description}

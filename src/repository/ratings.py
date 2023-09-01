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
from src.conf.messages import YOUR_PHOTO,ALREADY_LIKE
from src.database.models import User, Role, BlacklistToken, Post, Rating, Photo
from src.schemas import UserSchema, UserProfileSchema

async def create_photo(content:str, user:User,db:AsyncSession):
    new_photo = Photo(content=content,user_id=user.id)

    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)

    return new_photo


async def create_rating(rating: str,photos_id:str, user:User,db:AsyncSession):

    query = select(Rating).filter(Rating.user_id == user.id, 
                                  Rating.photo_id ==Photo.id,)
    result = await db.execute(query)
    exsist_photo = result.scalars().all()
    if exsist_photo!=[]:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ALREADY_LIKE
            ) 
    query=select(Photo).filter(Photo.user_id == user.id)
    res=await db.execute(query)
    your_photo=res.scalars().all()
    
    if your_photo   !=[]:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=YOUR_PHOTO
            ) 
    
    new_rating = Rating(rating=int(rating),user_id=user.id,photo_id=int(photos_id))
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)

    return new_rating

async def get_rating(photos_id:str,db:AsyncSession):

    query = select(Rating).filter(Rating.photo_id == int(photos_id))

    result = await db.execute(query)
    all_ratings = result.scalars().all()
    count_ratings=len(all_ratings)
    if count_ratings==0:
        return 0
    res=0
    for i in all_ratings:
        res+=i.rating

    average_rating = res / count_ratings
    return round(average_rating, 1)


async def get_all_ratings(photos_id:str,db:AsyncSession):

    query = select(Rating).filter(Rating.photo_id == int(photos_id))

    result = await db.execute(query)
    all_ratings = result.scalars().all()
    
    return all_ratings
    
async def delete_all_ratings(photos_id:str,user_id:str,db:AsyncSession):

    query = select(Rating).filter(Rating.photo_id == int(photos_id),
                                  Rating.user_id== int(user_id))
    

    result = await db.execute(query)
    rating_to_delete = result.scalar()

    if rating_to_delete:
        await db.delete(rating_to_delete) 
        await db.commit()
        return {"message": "Rating delete"}

    return {"message": "Rating dont find"}
    


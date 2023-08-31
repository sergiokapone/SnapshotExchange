from datetime import datetime

from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from src.conf.config import init_cloudinary
from src.conf.messages import USER_NOT_ACTIVE
from src.database.models import User, Role, BlacklistToken, Post, Rating, Photo
from src.schemas import UserSchema, UserProfileSchema

async def create_photo(rating: 0>= int <=5,photo:Photo, user:User,db:AsyncSession):
    pass


async def create_rating(rating: 0>= int <=5,photo:Photo, user:User,db:AsyncSession):
    query = select(Rating).filter(Rating.user_id == user.id, Rating.photo_id == photo.id)
    result = await db.execute(query)
    all_users = result.scalars().all()
    if all_users!=[]:
        return 'Ви вже поставили оцінку'
    return all_users



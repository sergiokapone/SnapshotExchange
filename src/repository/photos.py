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



async def get_URL(photo_id,db:AsyncSession):
    pass
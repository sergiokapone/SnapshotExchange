from datetime import datetime

from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from src.conf.config import init_cloudinary
from src.conf.messages import USER_NOT_ACTIVE
from src.database.models import User, Role, BlacklistToken, Post
from src.schemas import UserSchema, UserProfileSchema



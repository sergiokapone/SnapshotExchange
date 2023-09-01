import enum
from datetime import date

from sqlalchemy import Boolean, Column, DateTime,ForeignKey, Integer, Numeric, String, Table, Text, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import aggregated
from sqlalchemy import Enum

Base = declarative_base()


class Role(enum.Enum):
    user: str = 'User'
    moder: str = 'Moderator'
    admin: str = 'Administrator'


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] =  mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(String(500),nullable=True, unique=False)
    posts: Mapped['Post'] = relationship('Post', back_populates='user')
    ratings: Mapped['Rating'] = relationship('Rating', back_populates='user')
    photos: Mapped['Photo'] = relationship('Photo', back_populates='user')
    

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    photo:Mapped[str] = mapped_column(String(500), nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='posts')

class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ratings: Mapped['Rating'] = relationship('Rating', back_populates='photo')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='photos')
    content: Mapped[str] = mapped_column(String(200))

class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped['User'] = relationship('User', back_populates='ratings')

    rating: Mapped[int] = mapped_column(Integer)

    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'))
    photo: Mapped[int] = relationship('Photo', back_populates='ratings')



class BlacklistToken(Base):
    __tablename__ = 'blacklist_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    blacklisted_on : Mapped[date] = mapped_column(DateTime, default=func.now())

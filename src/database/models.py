import enum
from datetime import date

from sqlalchemy import Boolean, Column, DateTime,ForeignKey, Integer, Numeric, String, Table, Text, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import aggregated
from sqlalchemy import Enum

Base = declarative_base()


photo_m2m_tags = Table(
    'photo_m2m_tags',
    Base.metadata,
    Column('photo_id', Integer, ForeignKey('photos.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

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
    
    ratings: Mapped['Rating'] = relationship('Rating', back_populates='user')
    photos: Mapped['Photo'] = relationship('Photo', back_populates='user')
    

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    photo:Mapped[str] = mapped_column(String(500), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    

class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    
    ratings: Mapped['Rating'] = relationship('Rating', back_populates='photo', cascade='all, delete-orphan')
    tags: Mapped[list[str]] = relationship('Tag', secondary=photo_m2m_tags, backref='photos')
    QR: Mapped['QR_code'] = relationship('QR_code', back_populates='photo', cascade='all, delete-orphan')
    user: Mapped['User'] = relationship('User', back_populates='photos')


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    rating: Mapped[int] = mapped_column(Integer)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'))

    user: Mapped['User'] = relationship('User', back_populates='ratings')
    photo: Mapped[int] = relationship('Photo', back_populates='ratings')


class QR_code(Base):
    __tablename__ = "Qr_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)

    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'))
    photo: Mapped[int] = relationship('Photo', back_populates='QR')


class BlacklistToken(Base):
    __tablename__ = 'blacklist_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    blacklisted_on : Mapped[date] = mapped_column(DateTime, default=func.now())

class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=True)


class Comment(Base):
    __tablename__ = 'comments'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[int] = mapped_column(Text, nullable=False)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    photo_id: Mapped[int] = mapped_column('photo_id', ForeignKey('photos.id', ondelete='CASCADE'), default=None)
    update_status: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship('User', backref="comments")
    photo = relationship('Photo', backref="comments")
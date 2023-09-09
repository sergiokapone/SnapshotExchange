import enum
from datetime import date

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import aggregated
from sqlalchemy import Enum

from src.database.connect_db import Base
# Base = declarative_base()


class CropMode(str, enum.Enum):
    fill = "fill"
    thumb = "thumb"
    fit = "fit"
    limit = "limit"
    pad = "pad"
    scale = "scale"


class BGColor(str, enum.Enum):
    black = "black"
    white = "white"
    red = "red"
    green = "green"
    blue = "blue"
    yellow = "yellow"
    gray = "gray"
    brown = "brown"
    transparent = "transparent"


photo_m2m_tags = Table(
    "photo_m2m_tags",
    Base.metadata,
    Column("photo_id", Integer, ForeignKey("photos.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

class Role(enum.Enum):
    """
    User Roles Enumeration

    This enumeration defines the possible roles for users in the system.

    - `user`: Represents a regular user.
    - `moder`: Represents a moderator with additional privileges.
    - `admin`: Represents an administrator with full system control.

    Each role has a corresponding string value for easy identification.

    **Example Usage:**

    .. code-block:: python

        user_role = Role.user
        admin_role = Role.admin

    """

    user: str = "User"
    moder: str = "Moderator"
    admin: str = "Administrator"


class User(Base):
    """
    User Model

    SQLAlchemy model represents a user in the database.

    :param id: The unique identifier for the user (primary key).
    :param username: The username of the user (unique).
    :param email: The email address of the user (unique).
    :param password: The hashed password of the user.
    :param created_at: The timestamp when the user was created.
    :param updated_at: The timestamp when the user was last updated.
    :param avatar: The URL of the user's avatar image.
    :param refresh_token: The refresh token associated with the user.
    :param role: The role of the user ('User' or 'Adminisrtator', 'Voderator').
    :param confirmed: Indicates whether the user's email is confirmed.
    :param is_active: Indicates whether the user's account is active.
    :param description: A brief description or bio of the user.
    :param ratings: Relationship to user ratings.
    :param photos: Relationship to user's uploaded photos.

    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True, unique=False)

    ratings: Mapped["Rating"] = relationship("Rating", back_populates="user")
    photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="user")


class Photo(Base):

    """
    Photo Model

    This SQLAlchemy model represents a photo in the database.

    :param id: The unique identifier for the photo (primary key).
    :param url: The URL of the photo.
    :param description: A brief description of the photo.
    :param user_id: The user ID of the owner of the photo.
    :param created_at: The timestamp when the photo was created.
    :param cloud_public_id: The public ID of the photo in the cloud storage.
    :param ratings: Relationship to photo ratings.
    :param tags: Relationship to tags associated with the photo.
    :param QR: Relationship to QR codes associated with the photo.
    :param user: Relationship to the user who uploaded the photo.
    :param comments: Relationship to comments on the photo.

    """

    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    cloud_public_id: Mapped[str] = mapped_column(String, nullable=False)

    ratings: Mapped["Rating"] = relationship(
        "Rating", back_populates="photo", cascade="all, delete-orphan"
    )
    tags: Mapped[list[str]] = relationship(
        "Tag", secondary=photo_m2m_tags, backref="photos"
    )
    QR: Mapped["QR_code"] = relationship(
        "QR_code", back_populates="photo", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship("User", back_populates="photos")

    comments: Mapped["Comment"] = relationship(
        "Comment", back_populates="photo", cascade="all, delete-orphan"
    )


class Rating(Base):

    """
    Rating Model

    This SQLAlchemy model represents a rating given by a user to a photo in the database.

    :param id: The unique identifier for the rating (primary key).
    :param user_id: The user ID of the user who gave the rating.
    :param rating: The numerical rating value.
    :param photo_id: The photo ID of the photo that received the rating.
    :param user: Relationship to the user who gave the rating.
    :param photo: Relationship to the photo that received the rating.

    """

    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"))

    user: Mapped["User"] = relationship("User", back_populates="ratings")
    photo: Mapped[int] = relationship("Photo", back_populates="ratings")


class QR_code(Base):
    """
    QR_code Model

    This model represents a QR code associated with a photo in the system.

    :param int id: The unique identifier for the QR code (primary key).
    :param str url: The URL or identifier of the QR code.
    :param int photo_id: The ID of the associated photo (foreign key).

    **Example Usage:**

    .. code-block:: python

        new_qr_code = QR_code(
            url="https://example.com/qrcode123",
            photo_id=1
        )

    """

    __tablename__ = "Qr_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)

    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id"))
    photo: Mapped[int] = relationship("Photo", back_populates="QR")


class BlacklistToken(Base):
    """
    BlacklistToken Model

    This model represents a blacklisted token in the system, which is used to prevent token reuse.

    :param int id: The unique identifier for the blacklisted token (primary key).
    :param str token: The token string that has been blacklisted (unique and not nullable).
    :param datetime blacklisted_on: The date and time when the token was blacklisted (default is the current time).

    **Example Usage:**

    .. code-block:: python

        blacklisted_token = BlacklistToken(
            token="your_token_string_here"
        )

    """

    __tablename__ = "blacklist_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    blacklisted_on: Mapped[date] = mapped_column(DateTime, default=func.now())


class Tag(Base):
    """
    Tag Model

    This model represents a tag that can be associated with photos in the system.

    :param int id: The unique identifier for the tag (primary key).
    :param str name: The name of the tag (unique and nullable).

    **Example Usage:**

    .. code-block:: python

        tag = Tag(
            name="your_tag_name_here"
        )

    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(25), unique=True, nullable=True)


class Comment(Base):
    """
    Comment Model

    This model represents a comment left by a user on a photo in the system.

    :param int id: The unique identifier for the comment (primary key).
    :param str text: The text content of the comment (required).
    :param datetime created_at: The timestamp when the comment was created (automatically generated).
    :param datetime updated_at: The timestamp when the comment was last updated (automatically generated).
    :param int user_id: The user identifier associated with the comment (foreign key to 'users.id').
    :param int photo_id: The photo identifier associated with the comment (foreign key to 'photos.id', can be None).
    :param bool update_status: A boolean flag indicating if the comment has been updated (default is False).

    :type user: User
    :type photo: Photo

    **Example Usage:**

    .. code-block:: python

        comment = Comment(
            text="Your comment text here",
            user_id=1,
            photo_id=2  # Optional, can be None
        )

    """

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[int] = mapped_column(Text, nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    photo_id: Mapped[int] = mapped_column(
        "photo_id", ForeignKey("photos.id", ondelete="CASCADE"), default=None
    )
    update_status: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", backref="comments")
    photo: Mapped["Photo"] = relationship("Photo", back_populates="comments")

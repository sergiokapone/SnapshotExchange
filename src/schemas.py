from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from src.database.models import Role

class UserSchema(BaseModel):
    """
    Schema for user registration data.
    """
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=30)

    model_config = ConfigDict(
        json_schema_extra={
            "title": "User Schema",
            "description": "Schema for user registration data",
            "example": {
                "username": "sergiokapone",
                "email": "example@example.com",
                "password": "qwer1234",
            },
        }
    )

class UserUpdateSchema(BaseModel):
    """
    Schema for updating user data.
    """
    username: str = Field(min_length=5, max_length=25)

class PhotoRating(BaseModel):
    """
    Schema for adding a rating to a photo.
    """
    content: str


class CommentSchema(BaseModel):
    text: str = "some text"
    photo_id: int


class CommentList(BaseModel):
    limit: int = 10
    offset: int = 0
    photo_id: int


class CommentUpdateSchema(BaseModel):
    id: int
    text: str


class CommentResponse(BaseModel):
    username: str
    text: str
    photo_id: int


class CommentRemoveSchema(BaseModel):
    id: int


class Rating(BaseModel):
    user_id: int
    rating: int
    photo_id: int

class UserResponseSchema(BaseModel):
    """
    Schema for user response data.
    """
    id: int
    username: str
    email: str
    is_active: bool | None
    created_at: datetime

class UserProfileSchema(BaseModel):
    """
    Schema for user profile data.
    """
    username: str
    email: EmailStr
    avatar: str | None
    photos_count: int | None
    comments_count: int | None
    is_active: bool | None
    created_at: datetime

class UserDb(BaseModel):
    """
    Schema for user data retrieved from the database.
    """
    id: int
    username: str
    email: str
    avatar: str | None
    role: Role
    created_at: datetime
    description: str | None

class TokenSchema(BaseModel):
    """
    Schema for a token response.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RequestEmail(BaseModel):
    """
    Schema for requesting an email.
    """
    email: EmailStr

class RequestRole(BaseModel):
    """
    Schema for requesting a user role change.
    """
    email: EmailStr
    role: Role

class MessageResponseSchema(BaseModel):
    """
    Schema for a generic message response.
    """
    message: str = "This is a message"

class PhotosDb(BaseModel):
    """
    Schema for photo data retrieved from the database.
    """
    id: int
    url: str
    description: str | None
    user_id: int
    created_at: datetime

class CommentSchema(BaseModel):
    """
    Schema for creating a comment.
    """
    text: str = "some text"
    photo_id: int

class CommentList(BaseModel):
    """
    Schema for listing comments.
    """
    limit: int = 10
    offset: int = 0
    photo_id: int

class CommentUpdateSchema(BaseModel):
    """
    Schema for updating a comment.
    """
    id: int
    text: str

class CommentResponse(BaseModel):
    """
    Schema for a comment response.
    """
    username: str
    text: str
    photo_id: int

class CommentRemoveSchema(BaseModel):
    """
    Schema for removing a comment.
    """
    id: int
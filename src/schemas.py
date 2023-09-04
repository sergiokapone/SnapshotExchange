from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator

from src.database.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=30)

    model_config = ConfigDict(
        json_schema_extra={
            "title": "User Schema",
            "description": "Schema for user data",
            "example": {
                "username": "sergiokapone",
                "email": "example@example.com",
                "password": "qwer1234",
            },
        }
    )


class UserUpdateSchema(BaseModel):
    username: str = Field(min_length=5, max_length=25)


class PhotoRat(BaseModel):
    content: str


class Rating(BaseModel):
    user_id: int
    rating: int
    photo_id: int


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)




class UserProfileSchema(BaseModel):
    username: str
    email: EmailStr
    avatar: str | None
    photos_count: int | None
    comments_count: int | None
    is_active: bool | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None
    role: Role
    created_at: datetime
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class RequestRole(BaseModel):
    email: EmailStr
    role: Role


class MessageResponseSchema(BaseModel):
    message: str = "This is a message"


class PhotosDb(BaseModel):
    id: int
    url: str
    description: str | None
    user_id: int
    created_at: datetime
    # tags: list[str]

    model_config = ConfigDict(from_attributes = True)

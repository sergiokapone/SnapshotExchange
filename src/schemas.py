from datetime import datetime
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator

from src.database.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=30)

    model_config = ConfigDict(
        json_schema_extra = {
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
    content:str

class Rating(BaseModel):
    user_id:int
    rating:int
    photo_id:int

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool | None
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)

class UserProfileSchema(BaseModel):
    username: str
    email: EmailStr
    avatar: str | None
    post_count: int | None
    comment_count: int | None
    rates_count: int | None
    is_active: bool | None
    created_at: datetime


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None
    role: Role
    created_at: datetime
    description: str| None

    model_config = ConfigDict(from_attributes = True)

class UserProfile(BaseModel):
    username: str
    email: str
    avatar: str | None
    created_at: datetime
    count_posts : int 

    model_config = ConfigDict(from_attributes = True)

class UserResponseSchema(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class RequestRole(BaseModel):
    email: EmailStr
    role: Role
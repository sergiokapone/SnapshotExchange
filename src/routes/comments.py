from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import FORBIDDEN, DELETE_SUCCESSFUL, TOO_MANY_REQUESTS
from src.database.connect_db import get_db
from src.database.models import User, Photo, Role
from src.repository.comments import create_comment, update_comment, delete_comment, get_comments
from src.schemas import CommentSchema, CommentResponse, CommentUpdateSchema, CommentRemoveSchema
from src.services.auth import auth_service
from src.services.roles import Admin_Moder


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/publish", response_model=CommentResponse, status_code=status.HTTP_201_CREATED,
             description=TOO_MANY_REQUESTS,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def post_comment(content: CommentSchema, current_user: User = Depends(auth_service.get_authenticated_user),
                       db: AsyncSession = Depends(get_db)):
    comment = await create_comment(content.text, current_user, content.photo_id, db)
    return {"username": current_user.username, "text": comment.text, "photo_id": comment.photo_id}


@router.patch("/update", response_model=CommentResponse, status_code=status.HTTP_200_OK, )
async def change_comment(content: CommentUpdateSchema,
                         current_user: User = Depends(auth_service.get_authenticated_user),
                         db: AsyncSession = Depends(get_db)):
    comment = await update_comment(content.text, content.id, db)
    return {"username": current_user.username, "text": comment.text, "photo_id": comment.photo_id}


@router.get("/{content.photo_id}")
async def show_comment(limit: int, offset: int, photo_id: int,
                         current_user: User = Depends(auth_service.get_authenticated_user),
                       db: AsyncSession = Depends(get_db)):
    comments = await get_comments(limit, offset, photo_id, db)
    return {"comments": comments}


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(Admin_Moder)])
async def remove_comment(content: CommentRemoveSchema,
                         current_user: User = Depends(auth_service.get_authenticated_user),
                         db: AsyncSession = Depends(get_db)):
    await delete_comment(content.id, db)
    return {"detail": DELETE_SUCCESSFUL}

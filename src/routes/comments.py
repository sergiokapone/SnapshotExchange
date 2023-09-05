import  src.repository.comments as reposytory_comments
from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import FORBIDDEN, DELETE_SUCCESSFUL, TOO_MANY_REQUESTS
from src.database.connect_db import get_db
from src.database.models import User, Photo, Role
from src.schemas import (
    CommentSchema,
    CommentResponse,
    CommentUpdateSchema,
    CommentRemoveSchema,
)
from src.services.auth import auth_service
from src.services.roles import Admin_Moder


router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post(
    "/publish",
    # response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    description=TOO_MANY_REQUESTS,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def post_comment(
    photo_id: int = Form(...),
    text: str = Form(...),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    comment = await reposytory_comments.create_comment(text, current_user, photo_id, db)
    
    if comment:
        return comment
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch(
    "/update",
    # response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
async def change_comment(
    comment_id: int = Form(...),
    text: str = Form(...),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    
    # Check that the current user is the author of the comment
    comment = await reposytory_comments.update_comment(text, comment_id, db)
    if comment:
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return comment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    


@router.delete("/delete")
async def remove_comment(
    comment_id: int = Form(...),
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    comment = await reposytory_comments.get_comment(comment_id, db)
    
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if comment.user_id != current_user.id and current_user.role not in [Role.moder, Role.admin]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    await reposytory_comments.delete_comment(comment_id, db)
    return {"detail": DELETE_SUCCESSFUL}


@router.get("/photos/{photo_id}")
async def show_photo_comments(
    photo_id: int,
    limit: int = 0,
    offset: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    comments = await reposytory_comments.get_photo_comments(limit, offset, photo_id, db)
    return {"comments": comments}

@router.get("/users/{user_id}")
async def show_user_comments(
    user_id: int,
    limit: int = 0,
    offset: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    comments = await reposytory_comments.get_user_comments(limit, offset, user_id, db)
    return {"comments": comments}
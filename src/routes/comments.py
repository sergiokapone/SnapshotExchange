from fastapi import APIRouter, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.messages import FORBIDDEN, DELETE_SUCCESSFUL, TOO_MANY_REQUESTS
from src.database.connect_db import get_db
from src.database.models import User
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
    """
    Publish a new comment on a photo.

    This function allows users to create and publish new comments on a photo. It enforces a rate limit of 10 requests
    per minute. Users must be authenticated to perform this action. The function accepts the comment content, the current
    authenticated user, and a database session.

    :param content: CommentSchema: The content of the comment to be published.
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: The created comment.
    :rtype: CommentResponse
    """
    comment = await create_comment(content.text, current_user, content.photo_id, db)
    return {"username": current_user.username, "text": comment.text, "photo_id": comment.photo_id}


@router.patch("/update", response_model=CommentResponse, status_code=status.HTTP_200_OK, )
async def change_comment(content: CommentUpdateSchema,
                         current_user: User = Depends(auth_service.get_authenticated_user),
                         db: AsyncSession = Depends(get_db)):
    """
    Update an existing comment.

    This function allows users to update an existing comment. Users must be authenticated to perform this action.
    The function accepts the updated comment content, the current authenticated user, and a database session.

    :param content: CommentUpdateSchema: The updated content of the comment.
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: The updated comment.
    :rtype: CommentResponse
    """
    comment = await update_comment(content.text, content.id, current_user, db)
    if comment:
        return {"username": current_user.username, "text": comment.text, "photo_id": comment.photo_id}
    return {"details": FORBIDDEN}


@router.get("/{photo_id}")
async def show_comment(limit: int, offset: int, photo_id: int,
                         current_user: User = Depends(auth_service.get_authenticated_user),
                       db: AsyncSession = Depends(get_db)):
    """
    Retrieve comments for a specific photo.

    This function allows users to retrieve comments for a specific photo. Users can specify the number of comments to
    retrieve and the offset for pagination. The function accepts the limit, offset,
    current authenticated user, and a database session.

    :param limit: int: The maximum number of comments to retrieve.
    :param offset: int: The offset for pagination.
    :param photo_id: int: The ID of the photo to retrieve comments for.
    :param current_user: User: The currently authenticated user.
    :param db: AsyncSession: The database session.
    :return: A list of comments for the specified photo.
    :rtype: List[CommentResponse]
    """
    comments = await get_comments(limit, offset, photo_id, db)
    return {"comments": comments}


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(Admin_Moder)])
async def remove_comment(content: CommentRemoveSchema,
                         current_user: User = Depends(auth_service.get_authenticated_user),
                         db: AsyncSession = Depends(get_db)):
    """
    Delete an existing comment.

    This function allows administrators to delete an existing comment. Users must be authenticated as an administrator
    to perform this action. The function accepts the ID of the comment to delete,
    the current authenticated user, and a database session.

    :param content: CommentRemoveSchema: The ID of the comment to delete.
    :param current_user: User: The currently authenticated user (administrator).
    :param db: AsyncSession: The database session.
    :return: A message indicating that the comment has been deleted.
    :rtype: dict
    """
    await delete_comment(content.id, db)
    return {"details": DELETE_SUCCESSFUL}

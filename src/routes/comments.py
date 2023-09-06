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
    """
    Publish a comment on a photo.

    :param photo_id: ID of the photo to comment on.
    :type photo_id: int
    :param text: The text of the comment.
    :type text: str
    :param current_user: The authenticated user.
    :type current_user: User
    :param db: Database session.
    :type db: AsyncSession

    :return: Comment object if successful.
    :rtype: dict

    :raises HTTPException: If the comment could not be created.
    :rtype: HTTPException
    """
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
    """
    Update a comment.

    :param comment_id: ID of the comment to be updated.
    :type comment_id: int
    :param text: The new text for the comment.
    :type text: str
    :param current_user: The authenticated user.
    :type current_user: User
    :param db: Database session.
    :type db: AsyncSession

    :return: Updated comment if successful.
    :rtype: dict

    :raises HTTPException 404: If the comment does not exist.
    :raises HTTPException 403: If the current user is not the author of the comment.
    """
    
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
    """
    Delete a comment.

    :param comment_id: ID of the comment to be deleted.
    :type comment_id: int
    :param current_user: The authenticated user.
    :type current_user: User
    :param db: Database session.
    :type db: AsyncSession

    :return: A response indicating the success of the deletion.
    :rtype: dict

    :raises HTTPException 404: If the comment does not exist.
    :raises HTTPException 403: If the current user is not the author of the comment and is not a moderator or admin.
    """
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
    """
    Retrieve comments for a specific photo.

    :param photo_id: The ID of the photo for which comments are to be retrieved.
    :type photo_id: int
    :param limit: The maximum number of comments to retrieve (default is 0, which retrieves all).
    :type limit: int
    :param offset: The offset for paginating through comments (default is 10).
    :type offset: int
    :param current_user: The authenticated user.
    :type current_user: User
    :param db: Database session.
    :type db: AsyncSession

    :return: A dictionary containing the list of comments for the specified photo.
    :rtype: dict

    :raises HTTPException 404: If the photo does not exist.
    """
    
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
    """
    Retrieve comments for a specific user.

    :param user_id: The ID of the user for whom comments are to be retrieved.
    :type user_id: int
    :param limit: The maximum number of comments to retrieve (default is 0, which retrieves all).
    :type limit: int
    :param offset: The offset for paginating through comments (default is 10).
    :type offset: int
    :param current_user: The authenticated user.
    :type current_user: User
    :param db: Database session.
    :type db: AsyncSession

    :return: A dictionary containing the list of comments for the specified user.
    :rtype: dict

    :raises HTTPException 404: If the user does not exist.
    """
    
    comments = await reposytory_comments.get_user_comments(limit, offset, user_id, db)
    return {"comments": comments}

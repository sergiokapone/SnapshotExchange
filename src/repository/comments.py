from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Comment


async def create_comment(content: str, user: str, photos_id: int, db: AsyncSession):
    """
    Create a new comment for a photo in the database.

    :param content: The text of the comment
    :type content: str
    :param user: The user who is creating the rating.
    :type user: User
    :param photos_id: The ID of the photo to rate.
    :type photos_id: int
    :param db: The database session.
    :type db: AsyncSession
    :return: The created comment object.
    :rtype: Comment
    """
    comment = Comment(text=content, user=user, photo_id=photos_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def update_comment(text: str, id: int, user: User, db: AsyncSession):
    """
    Update a comment for comment author

    :param text: The text for updating the comment
    :type text: str
    :param id: The ID of the comment to update
    :type id: int
    :param user: The user to update the comment
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: The updated comment object.
    :rtype: Comment
    """
    comment = await db.get(Comment, id)
    if comment.user_id == user.id:
        comment.text = text
        comment.update_status = True
        await db.commit()
        await db.refresh(comment)
        return comment
    return None


async def delete_comment(comment_id: int, db: AsyncSession):
    """
    Delete a comment

    :param comment_id: The ID of the comment to update
    :type comment_id: int
    :param db: The database session.
    :type db: AsyncSession
    :return: The comment object.
    :rtype: Comment
    """
    comment = await db.get(Comment, comment_id)
    await db.delete(comment)
    await db.commit()
    return comment


async def get_comments(limit: int, offset: int, photos_id: int, db: AsyncSession):
    """
    Review comments by photo

    :param limit: limit of comments
    :type: int
    :param offset: offset of comments
    :type offset: int
    :param photos_id: The ID of the photo for which to retrieve ratings.
    :type photos_id: int
    :param db: The database session.
    :type db: AsyncSession
    :return: A list of comment objects.
    :rtype: List[Comment]
    """
    sq = select(Comment).filter_by(photo_id=photos_id).offset(offset).limit(limit)
    contacts = await db.execute(sq)
    result = contacts.scalars().all()
    return result

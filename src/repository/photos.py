import os
from typing import List

import qrcode
import uuid

import cloudinary
import cloudinary.uploader
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import File, HTTPException, status
from src.conf.config import init_cloudinary
from src.database.models import (
    User,
    Role,
    Rating,
    Photo,
    QR_code,
    Tag,
    Comment
)


# ------------------------------- ## TAGS ## ----------------------------------

async def get_or_create_tag(tag_name: str, db: AsyncSession) -> Tag:
    """
    .. function:: async def get_or_create_tag(tag_name: str, db: AsyncSession) -> Tag

    Get or Create Tag
    ------------------

    This function retrieves an existing tag with the specified name from the database or creates a new one if it doesn't exist.

    :param str tag_name: The name of the tag to retrieve or create.
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The existing or newly created Tag object.
    :rtype: Tag
    :raises Exception: Raises an exception if there's an issue with database operations.

    **Example Usage:**

    .. code-block:: python

        tag_name = "example_tag"
        async with get_db() as db:
            tag = await get_or_create_tag(tag_name, db)
            print(tag.name)  # Print the name of the existing or newly created tag.

    This function first attempts to retrieve an existing tag with the specified name from the database. If the tag exists, it returns that tag. If not, it creates a new tag with the provided name, adds it to the database, commits the transaction, and returns the newly created tag.


    """
    existing_tag = await db.execute(select(Tag).filter(Tag.name == tag_name))
    tag = existing_tag.scalar_one_or_none()

    # If the tag does not exist, create a new one
    if not tag:
        tag = Tag(name=tag_name)
        db.add(tag)
        await db.commit()
        await db.refresh(tag)

    return tag


async def get_photo_tags(photo_id: int, db: AsyncSession) -> list[str] | None:
    query = (
        select(Tag.name)
        .join(Photo.tags)
        .filter(Photo.id == photo_id)
    )

    """
    .. function:: async def get_photo_tags(photo_id: int, db: AsyncSession) -> list[str] | None

    Get Photo Tags
    ------------------

    This function retrieves a list of tags associated with a specific photo by its ID.

    :param int photo_id: The ID of the photo for which to retrieve tags.
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A list of tag names associated with the photo, or None if there are no tags.
    :rtype: list[str] | None
    :raises Exception: Raises an exception if there's an issue with database operations.

    **Example Usage:**

    .. code-block:: python

        photo_id = 123
        async with get_db() as db:
            tags = await get_photo_tags(photo_id, db)
            if tags:
                print(tags)  # Print the list of tag names associated with the photo.
            else:
                print("No tags found for the photo.")

    This function constructs a database query to retrieve tag names associated with a specific photo. If tags are found, it returns a list of tag names. If no tags are associated with the photo, it returns None.

    """

    result = await db.execute(query)
    tags = result.scalars().all()
    if tags:
        return tags
    return None


# ---------------------------- ## Comments ## ---------------------------------


async def get_photo_comments(photo_id: int, db: AsyncSession) -> list[dict]:
    query = (
        select(Comment.text, User.username)
        .join(User)
        .filter(Comment.photo_id == photo_id)
    )
    """
    .. function:: async def get_photo_comments(photo_id: int, db: AsyncSession) -> list[dict]

   Get Photo Comments
   ------------------

   This function retrieves a list of comments associated with a specific photo by its ID.

   :param int photo_id: The ID of the photo for which to retrieve comments.
   :param db: The asynchronous database session.
   :type db: AsyncSession
   :return: A list of dictionaries containing comment text and the username of the commenter.
   :rtype: list[dict]
   :raises Exception: Raises an exception if there's an issue with database operations.

   **Example Usage:**

   .. code-block:: python

      photo_id = 123
      async with get_db() as db:
          comments = await get_photo_comments(photo_id, db)
          if comments:
              for comment in comments:
                  print(f"Username: {comment['username']}")
                  print(f"Comment: {comment['text']}")
          else:
              print("No comments found for the photo.")

   This function constructs a database query to retrieve comments associated with a specific photo. It returns a list of dictionaries, where each dictionary contains the comment text and the username of the commenter.

    """
    result = await db.execute(query)
    comments = result.all()
    if comments:
        return [{"text": comment.text, "username": comment.username} for comment in comments]
    return []


# ----------------------------- ### CRUD ### ---------------------------------#
async def upload_photo(
        current_user: User,
        photo: File(),
        description: str | None,
        db: AsyncSession,
        width: int | None,
        height: int | None,
        crop_mode: str | None,
        rounding: int | None,
        background_color: str,
        rotation_angle: int | None,
        tags: List[str] = [],
) -> Photo:
    """
    Upload a photo to the cloud storage and create a database entry.

    :param current_user: The user who is uploading the photo.
    :type current_user: User
    :param photo: The photo file to upload.
    :type photo: File
    :param description: The description of the photo.
    :type description: str | None
    :param db: The database session.
    :type db: AsyncSession
    :param width: The desired width for the photo transformation.
    :type width: int | None
    :param height: The desired height for the photo transformation.
    :type height: int | None
    :param crop_mode: The cropping mode for the photo transformation.
    :type crop_mode: str | None
    :param rounding: The rounding mode for the photo transformation.
    :type rounding: int | None
    :param background_color: The background color for the photo transformation.
    :type background_color: str | None
    :param rotation_angle: The angle for the photo transformation.
    :type rotation_angle: int | None
    :param tags: A list of tags for the photo.
    :type tags: List[str]
    :return: True if the upload was successful, False otherwise.
    :rtype: bool
    """

    unique_photo_id = uuid.uuid4()
    public_photo_id = f"Photos_of_users/{current_user.username}/{unique_photo_id}"

    transformations = [{"width": width,
                        "height": height,
                        "angle": rotation_angle,
                        "background": background_color,
                        "radius": rounding,
                        }]
    if crop_mode is not None:
        transformations.append({"crop": crop_mode})

    init_cloudinary()

    uploaded_file_info = cloudinary.uploader.upload(
        photo.file, public_id=public_photo_id, overwrite=True,  transformation=transformations
    )

    photo_url = uploaded_file_info["secure_url"]
    public_id = uploaded_file_info["public_id"]

    # add photo url to DB
    photo_tags = []
    for tag_name in tags:
        existing_tag = await get_or_create_tag(tag_name, db)
        photo_tags.append(existing_tag)

    new_photo = Photo(url=photo_url,
                      cloud_public_id=public_id,
                      description=description,
                      user_id=current_user.id,
                      tags=photo_tags
                      )
    try:
        db.add(new_photo)
        await db.commit()
        await db.refresh(new_photo)
    except Exception as e:
        await db.rollback()
        raise e

    return new_photo


async def get_my_photos(
        skip: int, limit: int, current_user: User, db: AsyncSession
) -> list[Photo]:
    """
    The get_photos function returns a list of all photos of current_user from the database.

    :param skip: int: Skip the first n records in the database
    :param limit: int: Limit the number of results returned
    :param current_user: User
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of all photos
    """
    query = (
        select(Photo).where(Photo.user_id == current_user.id).offset(skip).limit(limit)
    )
    result = await db.execute(query)
    photos = result.scalars().all()
    return photos


async def get_photos(
        skip: int, limit: int, db: AsyncSession
) -> list[Photo]:
    """
    The get_photos function returns a list of all photos of current_user from the database.

    :param skip: int: Skip the first n records in the database
    :param limit: int: Limit the number of results returned
    :param current_user: User
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of all photos
    """
    query = (
        select(Photo)
        .join(Photo.tags)
        .options(selectinload(Photo.tags))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    photos = result.scalars().all()

    return photos


async def get_photo_by_id(photo_id: int, db: AsyncSession) -> dict:
    """
    Retrieve a photo by its ID from the database.

    :param photo_id: int: The ID of the photo to retrieve
    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary containing the details of the retrieved photo, or None if not found
    """
    query = select(Photo).filter(Photo.id == photo_id)
    result = await db.execute(query)
    photo = result.scalar_one_or_none()
    if photo:
        return photo


async def update_photo(
        current_user: User, photo_id: int,
        description: str,
        db: AsyncSession
) -> dict:
    """
    Update the description of a photo owned by the current user.

    :param current_user: User: The user who owns the photo
    :param photo_id: int: The ID of the photo to be updated
    :param description: str: The new description for the photo
    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary containing the updated photo's URL and description
    """
    query_result = await db.execute(
        select(Photo)
        .where(Photo.user_id == current_user.id)
        .where(Photo.id == photo_id)
    )
    photo = query_result.scalar()

    if photo:
        photo.description = description
        try:
            await db.commit()
            await db.refresh(photo)
            return photo
        except Exception as e:
            await db.rollback()
            raise e


async def remove_photo(photo_id: int, user: User, db: AsyncSession) -> bool:
    """
    Remove a photo from cloud storage and the database.

    :param photo_id: The ID of the photo to remove.
    :type photo_id: int
    :type user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: True if the removal was successful, False otherwise.
    :param user: The user who is removing the photo.
    :rtype: bool
    """

    query = select(Photo).filter(Photo.id == photo_id)
    result = await db.execute(query)
    photo = result.scalar_one_or_none()

    if not photo:
        return False

    if user.role == Role.admin or photo.user_id == user.id:
        # deleting from cloudinary
        init_cloudinary()
        cloudinary.uploader.destroy(photo.cloud_public_id)

        try:
            # Deleting linked ratings
            await db.execute(
                Rating.__table__.delete().where(Rating.photo_id == photo_id)
            )
            # Deleting linked photo
            await db.delete(photo)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise e


# --------------------------- ### END CRUD ### -------------------------------#


async def get_URL_Qr(photo_id: int, db: AsyncSession):
    """
    Generate and retrieve a QR code URL for a photo.

    :param photo_id: The ID of the photo for which to generate a QR code.
    :type photo_id: int
    :param db: The database session.
    :type db: AsyncSession
    :return: A dictionary containing the source URL and QR code URL.
    :rtype: dict
    """

    query = select(Photo).filter(Photo.id == photo_id)
    result = await db.execute(query)
    photo = result.scalar()

    if photo is None:
        raise HTTPException(status_code=404)

    query = select(QR_code).filter(QR_code.photo_id == photo_id)
    result = await db.execute(query)
    qr = result.scalar()

    if qr is not None:
        return {"source_url": photo.url, "qr_code_url": qr.url}

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(photo.url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_code_file_path = "my_qr_code.png"
    img.save(qr_code_file_path)

    init_cloudinary()
    upload_result = cloudinary.uploader.upload(
        qr_code_file_path,
        public_id=f"Qr_Code/Photo_{photo_id}",
        overwrite=True,
        invalidate=True,
    )
    qr = QR_code(url=upload_result["secure_url"], photo_id=photo_id)

    try:
        db.add(qr)
        await db.commit()
        await db.refresh(qr)
    except Exception as e:
        await db.rollback()
        print(e)

    os.remove(qr_code_file_path)

    return {"source_url": photo.url, "qr_code_url": qr.url}

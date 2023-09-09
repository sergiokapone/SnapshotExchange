from datetime import datetime

from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from src.conf.config import init_cloudinary
from src.database.models import User, Role, BlacklistToken, Photo, Comment
from src.schemas import UserSchema, UserProfileSchema


async def create_user(body: UserSchema, db: AsyncSession) -> User:
    """
    Create a new user in the database.

    :param body: The user data.
    :type body: UserSchema
    :param db: The database session.
    :type db: AsyncSession
    :return: The created user object.
    :rtype: User
    """
    try:
        g = Gravatar(body.email)
        g.get_image()
    except Exception as e:
        print(e)

    new_user = User(**body.model_dump())
    new_user.role = Role.user

    users_result = await db.execute(select(User))
    users_count = len(users_result.scalars().all())

    if not users_count:
        new_user.role = Role.admin

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        await db.rollback()
        raise e


async def edit_my_profile(
    file, new_description, new_username, user: User, db: AsyncSession
) -> User:
    """
    The edit_my_profile function allows a user to edit their profile.

    :param file: Upload the image to cloudinary
    :param new_username: Change the username of the user
    :param user: User: Get the user object from the database
    :param db: AsyncSession: Access the database
    :return: A user object
    """
    result = await db.execute(select(User).filter(User.id == user.id))
    me = result.scalar_one_or_none()
    if new_username:
        me.username = new_username
        me.description = new_description
    init_cloudinary()
    cloudinary.uploader.upload(
        file.file,
        public_id=f"Avatars/{me.username}",
        overwrite=True,
        invalidate=True,
    )
    url = cloudinary.CloudinaryImage(f"Avatars/{me.username}").build_url(
        width=250, height=250, crop="fill"
    )
    me.avatar = url

    try:
        await db.commit()
        await db.refresh(me)
        return me
    except Exception as e:
        await db.rollback()
        raise e


async def get_users(skip: int, limit: int, db: AsyncSession) -> list[User]:
    """
    The get_users function returns a list of all users from the database.

    :param skip: int: Skip the first n records in the database
    :param limit: int: Limit the number of results returned
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of all users
    """
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


async def get_user_profile(username: str, db: AsyncSession) -> User:
    """
    Get the profile of a user by username.

    :param username: The username of the user.
    :type username: str
    :param db: The database session.
    :type db: AsyncSession
    :return: The user profile.
    :rtype: User
    """

    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        # Count number of photos of user with username
        photos_query = select(func.count()).where(Photo.user_id == user.id)
        photos_result = await db.execute(photos_query)
        photos_count = photos_result.scalar()

        # Count number of comments  of user with username
        comments_query = select(func.count()).where(Comment.user_id == user.id)
        comments_result = await db.execute(comments_query)
        comments_count = comments_result.scalar()

        user_profile = UserProfileSchema(
            id=user.id,
            role=user.role,
            username=user.username,
            email=user.email,
            avatar=user.avatar,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            is_active=user.is_active,
            photos_count=photos_count,
            comments_count=comments_count,
        )
        return user_profile
    return None


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """
    The get_user_by_email function takes in an email and a database session, then returns the user with that email.

    :param email: str: Get the email from the user
    :param db: Session: Pass a database session to the function
    :return: A user object if the email is found in the database
    """
    try:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None


async def get_user_by_reset_token(reset_token: str, db: AsyncSession) -> User | None:
    """
    Retrieve a user by their reset token.

    This function queries the database to retrieve a user based on their reset token.

    :param reset_token: str: The reset token associated with the user.
    :param db: AsyncSession: The asynchronous database session.
    :return: The user if found, or None if not found.
    :rtype: User | None
    """

    try:
        result = await db.execute(
            select(User).filter(User.refresh_token == reset_token)
        )
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None


async def get_user_by_user_id(user_id: int, db: AsyncSession) -> User | None:
    """
    Get User by User ID

    This function retrieves a user by their user ID from the database.

    :param int user_id: The ID of the user to retrieve.
    :param AsyncSession db: An asynchronous database session.
    :return: The user with the specified ID, or None if the user is not found.
    :rtype: User | None
    """

    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None


async def get_user_by_username(username: str, db: AsyncSession) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session, then returns the user with that email.

    :param email: str: Get the email from the user
    :param db: Session: Pass a database session to the function
    :return: A user object if the email is found in the database
    """
    try:
        result = await db.execute(select(User).filter(User.username == username))
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None


async def update_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user that is being updated
    :param token: str | None: Store the token in the database
    :param db: Session: Create a database session
    :return: None, but the return type is specified as str | none
    """
    user.refresh_token = token
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def confirm_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.

    :param email: str: Get the email of the user that is trying to confirm their account
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def ban_user(email: str, db: AsyncSession) -> None:
    """
    The ban_user function takes in an email and a database session.
    It then finds the user with that email, sets their is_active field to False,
    and commits the change to the database.

    :param email: str: Identify the user to be banned
    :param db: Session: Pass in the database session
    :return: None, because we don't need to return anything
    """
    user = await get_user_by_email(email, db)
    user.is_active = False
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def activate_user(email: str, db: AsyncSession) -> None:
    """
    Activates a user account by setting their 'is_active' status to True.

    :param str email: The email address of the user to activate.
    :param AsyncSession db: The asynchronous database session.

    :return: None
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.is_active = True
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


async def make_user_role(email: str, role: Role, db: AsyncSession) -> None:
    """
    The make_user_role function takes in an email and a role, and then updates the user's role to that new one.
    Args:
    email (str): The user's email address.
    role (Role): The new Role for the user.

    :param email: str: Get the user by email
    :param role: Role: Set the role of the user
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.role = role
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e


#### BLACKLIST #####


async def add_to_blacklist(token: str, db: AsyncSession) -> None:
    """
    **Adds a token to the blacklist.**

    :param token: str: Pass the token to be blacklisted
    :param db: AsyncSession: Create a new session with the database
    :return: None
    """
    blacklist_token = BlacklistToken(token=token, blacklisted_on=datetime.now())

    try:
        db.add(blacklist_token)
        await db.commit()
        await db.refresh(blacklist_token)
    except Exception as e:
        await db.rollback()
        raise e


async def is_blacklisted_token(token: str, db: AsyncSession) -> bool:
    """
    Check if a Token is Blacklisted

    This function checks if a given token is blacklisted in the database.

    :param str token: The token to be checked.
    :param AsyncSession db: An asynchronous database session.
    :return: True if the token is blacklisted, False otherwise.
    :rtype: bool
    """

    result = await db.execute(
        select(BlacklistToken).filter(BlacklistToken.token == token)
    )

    blacklist_token = result.scalar_one_or_none()

    if blacklist_token:
        return True
    return False

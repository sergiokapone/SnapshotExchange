from datetime import datetime

from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from src.conf.config import init_cloudinary
from src.conf.messages import USER_NOT_ACTIVE
from src.database.models import User, Role, BlacklistToken, Post
from src.schemas import UserSchema, UserProfileSchema

async def create_user(body: UserSchema, db: AsyncSession) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
        
    new_user = User(**body.dict())
    
    users_result = await db.execute(select(User))
    users_count = len(users_result.scalars().all())
    
    if not users_count: #  First user always admin
        new_user.role = Role.admin
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    print("Done")
    return new_user


async def get_me(user: User, db: AsyncSession) -> User:
    """
    The get_me function returns the user object of the current logged in user.
    
    
    :param user: User: Get the user id
    :param db: Session: Access the database
    :return: A user object
    """
    try:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None


async def edit_my_profile(file, new_username, user: User, db: AsyncSession) -> User:
    """
    The edit_my_profile function allows a user to edit their profile.
    
    :param file: Upload the image to cloudinary
    :param new_username: Change the username of the user
    :param user: User: Get the user object from the database
    :param db: Session: Access the database
    :return: A user object
    """
    result = await db.execute(select(User).filter(User.id == user.id))
    me = result.scalar_one_or_none()
    if new_username:
        me.username = new_username
        
    init_cloudinary()
    cloudinary.uploader.upload(file.file, public_id=f'Photoshare/{me.username}',
                               overwrite=True, invalidate=True)
    url = cloudinary.CloudinaryImage(f'Photoshare/{me.username}')\
                        .build_url(width=250, height=250, crop='fill')
    me.avatar = url
    db.commit()
    db.refresh(me)
    return me


async def get_users(skip: int, limit: int, db: AsyncSession) -> list[User]:
    """
    The get_users function returns a list of users from the database.
    
    :param skip: int: Skip the first n records in the database
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database session to the function
    :return: A list of users
    """
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    all_users = result.scalars().all()
    return all_users



async def get_users_with_username(username: str, db: AsyncSession) -> list[User]:
    """
    The get_users_with_username function returns a list of users with the given username.
        Args:
            username (str): The username to search for.
            db (Session): A database session object.
        Returns:
            list[User]: A list of User objects that match the given criteria.
    
    :param username: str: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass the database session to the function
    :return: A list of users
    """
    return db.query(User).filter(func.lower(User.username).like(f'%{username.lower()}%')).all()

async def get_users_posts(skip: int, limit: int, db: AsyncSession) -> list[User]:
    """
    The get_users function returns a list of users from the database.
    
    :param skip: int: Skip the first n records in the database
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database session to the function
    :return: A list of users
    """
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    all_users = result.scalars().all()
    return all_users


async def get_user_profile(username: str, db: AsyncSession) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        post_count = db.query(Post).filter(Post.user_id == user.id).count()
        comment_count = db.query(Comment).filter(Comment.user_id == user.id).count()
        rates_count = db.query(Rating).filter(Rating.user_id == user.id).count()
        user_profile = UserProfileModel(
                username=user.username,
                email=user.email,
                avatar=user.avatar,
                created_at=user.created_at, 
                is_active=user.is_active,
                post_count=post_count,
                comment_count=comment_count,
                rates_count=rates_count
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
    
async def get_user_by_username(username: str, db: AsyncSession) -> User:
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
    db.commit()


async def confirm_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.

    :param email: str: Get the email of the user that is trying to confirm their account
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


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
    await db.commit()


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
    db.commit()


#### BLACKLIST #####

async def add_to_blacklist(token: str, db: AsyncSession) -> None:
    """
    The add_to_blacklist function adds a token to the blacklist.
        Args:
            token (str): The JWT that is being blacklisted.
            db (Session): The database session object used for querying and updating the database.
    
    :param token: str: Pass the token to be blacklisted
    :param db: Session: Create a new session with the database
    :return: None
    """
    blacklist_token = BlacklistToken(token=token, blacklisted_on=datetime.now())
    db.add(blacklist_token)
    db.commit()
    db.refresh(blacklist_token)
    
    
async def find_blacklisted_token(token: str, db: AsyncSession) -> None:
    """
    The find_blacklisted_token function takes a token and database session as arguments.
    It then queries the BlacklistToken table for any tokens that match the one passed in.
    If it finds a matching token, it returns that object.
    
    :param token: str: Pass the token to be checked
    :param db: Session: Connect to the database
    :return: A blacklisttoken object or none
    """
    
    try:
        result = await db.execute(select(BlacklistToken).filter(BlacklistToken.token == token))
        return result.scalar_one_or_none()
    except NoResultFound:
        return None
    
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    return blacklist_token
    
    
async def remove_from_blacklist(token: str, db: AsyncSession) -> None:
    """
    The remove_from_blacklist function removes a token from the blacklist.
        Args:
            token (str): The JWT to remove from the blacklist.
            db (Session): A database session object.
    
    :param token: str: Specify the token to be removed from the blacklist
    :param db: Session: Access the database
    :return: None
    """
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    db.delete(blacklist_token)

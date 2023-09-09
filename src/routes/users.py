### Import from FastAPI ###

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

### Import from Redis ###

from redis.asyncio import Redis  # As type

### Import from SQLAlchemy ###

from sqlalchemy.ext.asyncio import AsyncSession

### Import from Pydentic ###

from pydantic import EmailStr

### Import from Configurations ###

from src.conf.config import init_async_redis
from src.conf.messages import (
    NOT_FOUND,
    USER_ROLE_IN_USE,
    INVALID_EMAIL,
    USER_NOT_ACTIVE,
    USER_IS_ACTIVE,
    USER_ALREADY_NOT_ACTIVE,
    USER_ALREADY_ACTIVE,
    USER_CHANGE_ROLE_TO,
    USER_EXISTS,
    SELF_ACTIVATION,
)

### Import from Database ###

from src.database.connect_db import get_db
from src.database.models import User, Role

### Import from Schemas ###

from src.schemas import (
    UserProfileSchema,
    UserDb,
    MessageResponseSchema,
)

### Import from Repository ###

from src.repository import users as repository_users

### Import from Services ###

from src.services.roles import Admin_Moder_User, Admin
from src.services.auth import auth_service


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/get_me", response_model=UserDb)
async def read_my_profile(
    current_user: User = Depends(auth_service.get_authenticated_user),
):
    """
    **Get the profile of the current user.**

    This route retrieves the profile of the current authenticated user.

    Level of Access:

    - Current authorized user

    :param current_user: User: The current authenticated user.
    :return: Current user profile.
    :rtype: UserDb
    """
    return current_user


@router.patch("/edit_me", status_code=status.HTTP_200_OK, response_model=UserDb)
async def edit_my_profile(
    avatar: UploadFile = File(),
    new_username: str = Form(None),
    new_description: str = Form(None),
    current_user: User = Depends(auth_service.get_authenticated_user),
    redis_client: Redis = Depends(init_async_redis),
    db: AsyncSession = Depends(get_db),
):
    """
    **Edit the current user's profile.**

    This route allows the current user to edit own profile, including uploading an avatar, changing the username and description.

    Level of Access:
    - Current authorized user

    :param avatar: UploadFile: User avatar file (optional).

    :param new_username: str: New username (optional).

    :param new_description: str: New user description (optional).

    :param current_user: User: Current authenticated user.

    :param redis_client: Redis: Redis client.

    :param db: AsyncSession: Database session.

    :return: Updated user profile.

    :rtype: UserDb

    :raises: HTTPException with code 400 and detail "USER_EXISTS" if the new username already exists.
    """

    # Removing a key from Redis
    key_to_clear = f"user:{current_user.email}"
    await redis_client.delete(key_to_clear)

    other_user = await repository_users.get_user_by_username(new_username, db)

    if other_user is None:
        updated_user = await repository_users.edit_my_profile(
            avatar, new_description, new_username, current_user, db
        )

        return updated_user

    raise HTTPException(status_code=400, detail=USER_EXISTS)


@router.get(
    "/get_all",
    response_model=list[UserDb],
    dependencies=[Depends(Admin_Moder_User)],
)
async def get_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    **Get a list of users.**

    This route allows  to get a list of pagination-aware users.

    Level of Access:

    - Current authorized user

    :param skip: int: Number of users to skip.

    :param limit: int: Maximum number of users to return.

    :param current_user: User: Current authenticated user.

    :param db: AsyncSession: Database session.

    :return: List of users.

    :rtype: List[UserDb]
    """

    users = await repository_users.get_users(skip, limit, db)
    return users


@router.get("/{username}", response_model=UserProfileSchema)
async def user_profile(
    username: str,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> dict | None:
    """
    **Get a user's profile by username.**

    This route allows to retrieve a user's profile by their username.

    Level of Access:

    - Current authorized user

    :param username: str: The username of the user whose profile is to be retrieved.

    :param current_user: User: The current authenticated user (optional).

    :param db: AsyncSession: Database session.

    :return: User profile or None if no user is found.

    :rtype: dict | None

    :raises: HTTPException with code 404 and detail "NOT_FOUND" if the user is not found.
    """

    user = await repository_users.get_user_by_username(username, db)

    if user:
        urer_profile = await repository_users.get_user_profile(user.username, db)
        return urer_profile
    else:
        raise HTTPException(status_code=404, detail=NOT_FOUND)


@router.patch(
    "/ban",
    name="ban_user",
    dependencies=[Depends(Admin)],
    response_model=MessageResponseSchema,
)
async def ban_user(
    email: EmailStr,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    **Block a user by email.**

    This route allows to block a user by their email.

    Level of Access:

    - Administartor

    :param email: EmailStr: Email of the user to block.

    :param db: AsyncSession: Database session.

    :return: Successful user blocking message or error message.
    :rtype: dict
    """

    user = await repository_users.get_user_by_email(email, db)

    if not user:
        raise HTTPException(status_code=404, detail=INVALID_EMAIL)

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=SELF_ACTIVATION,
        )

    if user.is_active:
        await repository_users.ban_user(user.email, db)

        return {"message": USER_NOT_ACTIVE}
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE
        )


@router.patch(
    "/activate",
    name="activate_user",
    dependencies=[Depends(Admin)],
    response_model=MessageResponseSchema,
)
async def activate_user(
    email: EmailStr,
    current_user: User = Depends(auth_service.get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    """
    **Activate a user by email.**

    This route allows to activate a user by their email.

    Level of Access:

    - Administartor

    :param email: EmailStr: Email of the user to activate.

    :param db: AsyncSession: Database session.

    :return: Successful user blocking message or error message.
    :rtype: dict
    """

    user = await repository_users.get_user_by_email(email, db)

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=SELF_ACTIVATION,
        )

    if not user:
        raise HTTPException(status_code=404, detail=INVALID_EMAIL)

    if not user.is_active:
        await repository_users.activate_user(user.email, db)

        return {"message": USER_IS_ACTIVE}
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_ACTIVE
        )


@router.patch(
    "/asign_role/{role}",
    dependencies=[Depends(Admin)],
    response_model=MessageResponseSchema,
)
async def assign_role(
    email: EmailStr,
    role: Role,
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(init_async_redis),
):
    """
    **Assign a role to a user by email.**

    This route allows to assign the selected role to a user by their email.

    Level of Access:

    - Administartor

    :param email: EmailStr: Email of the user to whom you want to assign the role.

    :param selected_role: Role: The selected role for the assignment (Administrator, Moderator or User).

    :param db: AsyncSession: Database Session.

    :param redis_client: Redis: Redis client.

    :return: Message about successful role change.

    :rtype: dict
    """

    # Removing a key from Redis
    key_to_clear = f"user:{email}"
    await redis_client.delete(key_to_clear)

    user = await repository_users.get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL
        )

    if role == user.role:
        return {"message": USER_ROLE_IN_USE}
    else:
        await repository_users.make_user_role(email, role, db)
        return {"message": f"{USER_CHANGE_ROLE_TO} {role.value}"}

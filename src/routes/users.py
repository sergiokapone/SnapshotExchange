from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import users as repository_users
from src.database.models import User, Role

from src.schemas import (
    UserProfile,
    UserProfileSchema,
    UserResponseSchema,
    RequestEmail,
    UserDb,
    RequestRole,
)


from src.services.auth import auth_service

from src.services.roles import RoleChecker

from src.conf.messages import (
    NOT_FOUND,
    USER_ROLE_EXISTS,
    INVALID_EMAIL,
    USER_NOT_ACTIVE,
    USER_ALREADY_NOT_ACTIVE,
    USER_CHANGE_ROLE_TO,
)


router = APIRouter(prefix="/users", tags=["Users"])

# Permissions to use routes by role

allowed_get_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_create_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_get_all_users = RoleChecker([Role.admin])
allowed_remove_user = RoleChecker([Role.admin])
allowed_ban_user = RoleChecker([Role.admin])
allowed_change_user_role = RoleChecker([Role.admin])


@router.get("/get_me/", response_model=UserDb)
async def read_my_profile(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.put("/edit_me/", response_model=UserDb)
async def edit_my_profile(
    avatar: UploadFile = File(),
    new_username: str = Form(None),
    new_description: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    updated_user = await repository_users.edit_my_profile(
        avatar,new_description, new_username, current_user, db
    )
    return updated_user

@router.get("/{username}", response_model=UserProfile)
async def username_profile(username: str, db: AsyncSession = Depends(get_db)):
    user= await repository_users.get_user_by_username(username,db)
    count_posts= await repository_users.get_users_posts(user.id,db)
    result_dict= {"username": user.username,
                  "created_at":user.created_at,
                  "avatar":user.avatar,
                  "count_posts":count_posts}
    return result_dict

@router.get(
    "/get_all",
    response_model=list[UserDb],
    dependencies=[Depends(allowed_get_all_users)],
)
async def read_all_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    users = await repository_users.get_users(skip, limit, db)
    return users


@router.patch("/ban/{email}/", dependencies=[Depends(allowed_ban_user)])
async def ban_user_by_email(body: RequestEmail, db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL
        )

    if user.is_active:
        await repository_users.ban_user(user.email, db)

        return {"message": USER_NOT_ACTIVE}
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE
        )


@router.patch("/make_role/{email}/", dependencies=[Depends(allowed_change_user_role)])
async def make_role_by_email(body: RequestRole, db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL
        )

    if body.role == user.role:
        return {"message": USER_ROLE_EXISTS}
    else: 
        await repository_users.make_user_role(body.email, body.role, db)

        return {"message": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connect_db import get_db
from src.repository import photos as res_photos
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


router = APIRouter(prefix="/photos", tags=["Photos"])

# Permissions to use routes by role

allowed_get_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_create_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_get_all_users = RoleChecker([Role.admin])
allowed_remove_user = RoleChecker([Role.admin])
allowed_ban_user = RoleChecker([Role.admin])
allowed_change_user_role = RoleChecker([Role.admin])










@router.post("/make_URL_QR/", dependencies=[Depends(allowed_change_user_role)])
async def make_URL_QR(photo_id: RequestRole, db: AsyncSession = Depends(get_db)):
    
    url = await res_photos.get_URL(body.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL
        )

    if body.role == user.role:
        return {"message": USER_ROLE_EXISTS}
    else:
        await repository_users.make_user_role(body.email, body.role, db)

        return {"message": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}
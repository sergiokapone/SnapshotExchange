from fastapi import Depends, HTTPException, status, Request

from src.database.models import User, Role
from src.services.auth import auth_service

from src.conf.messages import OPERATION_FORBIDDEN
class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: User = Depends(auth_service.get_authenticated_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=OPERATION_FORBIDDEN)


allowed_get_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_create_user = RoleChecker([Role.admin, Role.moder, Role.user])
allowed_get_all_users = RoleChecker([Role.admin])
allowed_remove_user = RoleChecker([Role.admin])
allowed_ban_user = RoleChecker([Role.admin])
allowed_change_user_role = RoleChecker([Role.admin])
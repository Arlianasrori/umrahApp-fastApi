from fastapi import Cookie, Request
from sqlalchemy import and_
from ....models.user_model import User
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os
from ....types.user_types import UserRoleEnum

# Secret key for JWT token verification
SECRET_KEY = os.getenv("USER_SECRET_ACCESS_TOKEN")

async def superAdminAuth(access_token: str | None = Cookie(None), req: Request = None, Session: sessionDepedency = None):
    if not access_token:
        raise HttpException(status=401, message="invalid token(unauthorized)")
    try:
        # Decode and verify JWT token
        superAdmin = jwt.decode(access_token, SECRET_KEY, algorithms="HS256")
        print(superAdmin)

        if not superAdmin:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Query database for superAdmin user
        findsuperAdmin = (await Session.execute(select(User).where(and_(User.id == superAdmin["id"],User.role == UserRoleEnum.SUPER_ADMIN.value)))).scalar_one_or_none()

        if not findsuperAdmin:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Attach superAdmin info to request object
        req.superAdmin = findsuperAdmin.__dict__
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))

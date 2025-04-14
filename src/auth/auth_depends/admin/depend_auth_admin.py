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

async def adminAuth(access_token: str | None = Cookie(None), req: Request = None, Session: sessionDepedency = None):
    if not access_token:
        raise HttpException(status=401, message="invalid token(unauthorized)")
    try:
        # Decode and verify JWT token
        admin = jwt.decode(access_token, SECRET_KEY, algorithms="HS256")
        # print(admin)

        if not admin:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Query database for admin user
        findAdmin = (await Session.execute(select(User).where(and_(User.id == admin["id"],User.role == UserRoleEnum.ADMIN.value)))).scalar_one_or_none()

        if not findAdmin:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Attach admin info to request object
        req.admin = findAdmin.__dict__
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))

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
SECRET_KEY = os.getenv("USER_SECRET_REFRESH_TOKEN")

async def allUserRefreshAuth(refresh_token: str | None = Cookie(None), req: Request = None, Session: sessionDepedency = None):
    print(refresh_token)
    if not refresh_token:
        raise HttpException(status=401, message="invalid token(unauthorized)")
    try:
        # Decode and verify JWT token
        user = jwt.decode(refresh_token, SECRET_KEY, algorithms="HS256")

        if not user:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Query database for admin user
        findUser = (await Session.execute(select(User).where(and_(User.id == user["id"])))).scalar_one_or_none()

        if not findUser:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Attach admin info to request object
        req.User = findUser.__dict__
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))

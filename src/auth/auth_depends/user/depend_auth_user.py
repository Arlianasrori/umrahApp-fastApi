from fastapi import Cookie, Request, Header
from sqlalchemy import and_,or_
from ....models.user_model import User
from ....error.errorHandling import HttpException
from ....db.sessionDepedency import sessionDepedency
from jose import JWTError, jwt
from sqlalchemy import select
import os
from ....types.user_types import UserRoleEnum

# Secret key for JWT token verification
SECRET_KEY = os.getenv("USER_SECRET_ACCESS_TOKEN")

async def userAuth(access_token: str | None = Cookie(None),Authorization: str | None = Header(default=None, example="jwt access token"), req: Request = None, Session: sessionDepedency = None):
    try:
        token = None
        if access_token:
            token = access_token
        elif Authorization:
            token = Authorization.split(" ")[1]
        
        print(Authorization)
        # Check if a token is present
        if not token:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        # Decode and verify JWT token
        user = jwt.decode(token, SECRET_KEY, algorithms="HS256")

        if not user:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        # Query database for admin user
        findUser = (await Session.execute(select(User).where(and_(User.id == user["id"],or_(User.role == UserRoleEnum.USER.value, User.role == UserRoleEnum.ADMIN.value))))).scalar_one_or_none()

        if not findUser:
            raise HttpException(status=401, message="invalid token(unauthorized)")
        
        if not findUser.verified :
            raise HttpException(401, "user not verified")
        
        # Attach admin info to request object
        req.User = findUser.__dict__
    except JWTError as error:
        # Handle JWT decoding errors
        raise HttpException(status=401, message=str(error.args[0]))

from jose import jwt, JWTError
from sqlalchemy import select
import os
from ..models.user_model import User
from ..db.sessionDepedency import SessionLocal

SECRET_KEY = os.getenv("USER_SECRET_ACCESS_TOKEN")

async def socket_auth_middleware(auth):
    async with SessionLocal() as session: 
        if not auth or type(auth) != dict:
            return False
        
        auth_header = auth.get('access_token')
        if not auth_header:
            return False

        if type(auth_header) == str :
            token = auth_header
        else :
            scheme, _, token = auth_header.partition(' ')
        
        
        if not token:
            return False
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            if not payload:
                return False
            
            user_id = payload.get("id")
            
            findUser = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()

            if findUser is None or not findUser.verified:
                return False
            
            return {
                "id_user" : user_id,
            }
        except JWTError:
            return False
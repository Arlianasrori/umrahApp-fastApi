from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import UploadFile

# models 
from ....models.user_model import User
# schemas
from ...schemas.user_schema import UserBase
from .authProfileModel import UpdateProfileRequest
# types
from ....types.user_types  import UserRoleEnum
# common
from ....error.errorHandling import HttpException
from ....utils.updateTable_util import updateTable

async def getUser(id_user : int,session : AsyncSession) -> UserBase :
    findUser = (await session.execute(select(User).where(and_(User.id == id_user,User.role == UserRoleEnum.USER)))).scalar_one_or_none()
    if not findUser :
        raise HttpException(404,f"user tidak ditemukan")

    return {
        "msg" : "success",
        "data" : findUser
    }

async def updateProfile(id_user : int,profile : UpdateProfileRequest,session : AsyncSession) -> UserBase :
    findUser = (await session.execute(select(User).where(and_(User.id == id_user,User.role == UserRoleEnum.USER)))).scalar_one_or_none()
    if not findUser :
        raise HttpException(404,f"user tidak ditemukan")
    
    if profile.model_dump(exclude_none=True,exclude={"foto_profile"}) :
        updateTable(profile.model_dump(exclude={"foto_profile"}),findUser)

    

    return {
        "msg" : "success",
        "data" : findUser
    }
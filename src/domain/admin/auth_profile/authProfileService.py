from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

# models 
from ....models.user_model import User
# schemas
from ...schemas.user_schema import UserBase
# types
from ....types.user_types  import UserRoleEnum
# common
from ....error.errorHandling import HttpException

async def getAdmin(id_admin : int,session : AsyncSession) -> UserBase :
    findAdmin = (await session.execute(select(User).where(and_(User.id == id_admin,User.role == UserRoleEnum.ADMIN)))).scalar_one_or_none()
    if not findAdmin :
        raise HttpException(404,f"admin tidak ditemukan")

    return {
        "msg" : "success",
        "data" : findAdmin
    }

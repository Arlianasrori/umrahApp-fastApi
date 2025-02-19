from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_

# models
from ....models.user_model import User

# schemas
from .userSchema import ResponseSiswaPag
from ...schemas.user_schema import UserBase

# types
from ....types.user_types import UserRoleEnum

# common
import aiofiles
from copy import deepcopy
import math
from ....error.errorHandling import HttpException

async def getAllUser(page : int | None,session : AsyncSession) -> list[UserBase] | ResponseSiswaPag :
    statementSelectSiswa = select(User).where(User.role == UserRoleEnum.SISWA)

    if page :
        findUser = (await session.execute(statementSelectSiswa.limit(10).offset(10 * (page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(User.id).filter(User.role == UserRoleEnum.SISWA))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findUser,
                "count_data" : len(findUser),
                "count_page" : countPage
            }
        }
    else :
        findUser = (await session.execute(statementSelectSiswa)).scalars().all()
        print(findUser)
        return {
            "msg" : "success",
            "data" : findUser
        }

async def getSiswaById(id_user : int,session : AsyncSession) -> UserBase :
    findUser = (await session.execute(select(User).where(and_(User.id == id_user,User.role == UserRoleEnum.SISWA)))).scalar_one_or_none()
    if not findUser :
        raise HttpException(400,f"User dengan id {id_user} tidak ditemukan")
    return {
        "msg" : "success",
        "data" : findUser
    }

async def deleteUser(id_user : int,session : AsyncSession) -> UserBase :
    findUser = (await session.execute(select(User).where(and_(User.id == id_user,User.role == UserRoleEnum.SISWA)))).scalar_one_or_none()
    if not findUser :
        raise HttpException(400,f"User dengan id {id_user} tidak ditemukan")
    
    userDictCopy = deepcopy(findUser.__dict__)
    await session.delete(findUser)
    await session.commit()
    return {
        "msg" : "success",
        "data" : userDictCopy
    }
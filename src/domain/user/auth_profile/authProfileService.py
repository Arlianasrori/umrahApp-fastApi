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
from ....utils.generateId_util import generate_id
import os
from multiprocessing import Process
import aiofiles
from copy import deepcopy

async def getUser(id_user : int,session : AsyncSession) -> UserBase :
    findUser = (await session.execute(select(User).where(and_(User.id == id_user,User.role == UserRoleEnum.USER)))).scalar_one_or_none()
    if not findUser :
        raise HttpException(404,f"user tidak ditemukan")

    return {
        "msg" : "success",
        "data" : findUser
    }
  
FOTO_PROFILE_STORE = os.getenv("USER_PROFILE_BASE_STORE")
FOTO_PROFILE_BASE_URL = os.getenv("USER_PROFILE_BASE_URL")
async def updateProfile(id_user : int,profile : UpdateProfileRequest,session : AsyncSession) -> UserBase :
    findUser = (await session.execute(select(User).where(and_(User.id == id_user,User.role == UserRoleEnum.USER)))).scalar_one_or_none()
    if not findUser :
        raise HttpException(404,f"user tidak ditemukan")
    
    if profile.model_dump(exclude_none=True,exclude={"foto_profile"}) :
        updateTable(profile.model_dump(exclude={"foto_profile"}),findUser)

    if profile.foto_profile :
        ext_file = profile.foto_profile.split(".")
        if ext_file[-1] not in ["jpg","png","jpeg"] :
            raise HttpException(400,f"file harus berupa gambar")

        file_name = f"{generate_id()}-{profile.foto_profile.split(' ')[0]}.{ext_file[-1]}"
        file_name_save = f"{FOTO_PROFILE_STORE}{file_name}"
        file_name_before = None
        if findUser.foto_profile :
            file_name_before = deepcopy(findUser.foto_profile.split("/")[-1])

        async with aiofiles.open(file_name_save, "wb") as f:
            await f.write(profile.foto_profile.file.read())
            findUser.foto_profile = f"{FOTO_PROFILE_BASE_URL}/{file_name}"

            if file_name_before :
                remove_image_process = Process(target=os.remove, args=(f"{FOTO_PROFILE_STORE}{file_name_before}",))
                remove_image_process.start()

    userDictCopy = deepcopy(findUser.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : userDictCopy
    }
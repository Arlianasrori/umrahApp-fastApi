from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

# models 
from ...models.user_model import User
# schemas
from .superAdminSchema import AddAdminRequest,UpdateAdminRequest
from ..schemas.user_schema import UserBase
# types
from ...types.user_types  import UserRoleEnum
# common
from ...error.errorHandling import HttpException
from ...utils.generateId_util import generate_id
from ...auth.bcrypt.bcrypt import create_hash_password
import os
import aiofiles
from ...utils.updateTable_util import updateTable
from copy import deepcopy
from multiprocessing import Process

# auth-profile
async def getSuperAdmin(id_super_admin : int,session : AsyncSession) -> UserBase :
    findSuperAdmin = (await session.execute(select(User).where(and_(User.id == id_super_admin,User.role == UserRoleEnum.SUPER_ADMIN)))).scalar_one_or_none()
    if not findSuperAdmin :
        raise HttpException(404,f"super admin tidak ditemukan")

    return {
        "msg" : "success",
        "data" : findSuperAdmin
    }

# admin
FOTO_PROFILE_STORE = os.getenv("USER_PROFILE_BASE_STORE")
FOTO_PROFILE_BASE_URL = os.getenv("USER_PROFILE_BASE_URL")
async def addAdmin(admin : AddAdminRequest,session : AsyncSession) -> UserBase:
    findUserByEmail = (await session.execute(select(User).where(User.email == admin.email))).scalar_one_or_none()

    if findUserByEmail :
        raise HttpException(400,"email already exist")
    
    adminMapping = admin.model_dump(exclude={"foto_profile"})
    adminMapping.update({"id" : generate_id(),"role" : UserRoleEnum.SUPER_ADMIN.value,"verified" : True,"password" : create_hash_password(adminMapping["password"])})

    if admin.foto_profile :
        ext_file = admin.foto_profile.filename.split(".")

        if ext_file[-1] not in ["jpg","png","jpeg"] :
            raise HttpException(400,f"file harus berupa gambar")

        file_name = f"{generate_id()}-{admin.foto_profile.filename.split(' ')[0].split('.')[0]}.{ext_file[-1]}"
        file_name_save = f"{FOTO_PROFILE_STORE}{file_name}"

        async with aiofiles.open(file_name_save, "wb") as f:
            await f.write(admin.foto_profile.file.read())
            adminMapping["foto_profile"] = f"{FOTO_PROFILE_BASE_URL}/{file_name}"

    session.add(User(**adminMapping))
    await session.commit()
    return {
        "msg" : "success",
        "data" : adminMapping
    }

async def updateAdmin(id_admin : int,admin : UpdateAdminRequest,session:AsyncSession) -> UserBase:
    findAdmin = (await session.execute(select(User).where(and_(User.id == id_admin,User.role == UserRoleEnum.ADMIN)))).scalar_one_or_none()
    if not findAdmin :
        raise HttpException(404,f"admin not found")
    
    if admin.email :
        findUserByEmail = (await session.execute(select(User).where(User.email == admin.email, User.id != id_admin))).scalar_one_or_none()

        if findUserByEmail is None :
            raise HttpException(400,"email already exist")

    if admin.model_dump(exclude_none=True,exclude={"foto_profile"}) :
        updateTable(admin.model_dump(exclude={"foto_profile"}),findAdmin)

    if admin.foto_profile :
        ext_file = admin.foto_profile.filename.split(".")
        if ext_file[-1] not in ["jpg","png","jpeg"] :
            raise HttpException(400,f"file harus berupa gambar")

        file_name = f"{generate_id()}-{admin.foto_profile.filename.split(' ')[0]}.{ext_file[-1]}"
        file_name_save = f"{FOTO_PROFILE_STORE}{file_name}"
        file_name_before = findAdmin.foto_profile.split("/")[-1]

        async with aiofiles.open(file_name_save, "wb") as f:
            await f.write(admin.foto_profile.file.read())
            findAdmin.foto_profile = f"{FOTO_PROFILE_BASE_URL}/{file_name}"

    adminDictCopy = deepcopy(findAdmin.__dict__)
    await session.commit()
    if admin.foto_profile :
        remoove_image_process = Process(target=os.remove, args=(f"{FOTO_PROFILE_STORE}{file_name_before}",))
        remoove_image_process.start()

    return {
        "msg" : "success",
        "data" : adminDictCopy
    }
    
async def deleteAdmin(id_admin : int,session:AsyncSession) -> UserBase:
    findAdmin = (await session.execute(select(User).where(and_(User.id == id_admin, User.role == UserRoleEnum.ADMIN)))).scalar_one_or_none()
    if not findAdmin :
        raise HttpException(404,f"admin not found")

    adminDictCopy = deepcopy(findAdmin.__dict__)
    await session.delete(findAdmin)
    await session.commit()
    return {
        "msg" : "success",
        "data" : adminDictCopy
    }

async def getAllAdmin(session:AsyncSession) -> list[UserBase]:
    findAdmin = (await session.execute(select(User).where(and_(User.role == UserRoleEnum.ADMIN)))).scalars().all()

    return {
        "msg" : "success",
        "data" : findAdmin
    }

async def getAdminById(id_admin : int,session:AsyncSession) -> UserBase:
    findAdmin = (await session.execute(select(User).where(and_(User.id == id_admin, User.role == UserRoleEnum.ADMIN)))).scalar_one_or_none()

    if not findAdmin :
        raise HttpException(404,f"admin not found")

    return {
        "msg" : "success",
        "data" : findAdmin
    }
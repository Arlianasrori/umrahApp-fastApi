from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_,or_, text

# schemas
from .authSchema import LoginRequest,LoginResponse,RefreshTokenResponse,ForgotPasswordResponse,RegisterRequest,LoginOauth2Response
from ..schemas.user_schema import UserBase
# models
from ...models.user_model import User, OtpCode

# types
from ...types.user_types import UserRoleEnum

# common
from ...error.errorHandling import HttpException
from ...auth.bcrypt.bcrypt import verify_hash_password
from ...auth.token.create_token import create_token
from ...utils.sendOtp_util import sendOtp
from ...utils.generateId_util import generate_id
from datetime import datetime,timedelta
from ...auth.bcrypt.bcrypt import create_hash_password
from python_random_strings import random_strings
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from enum import Enum
import aiofiles

class PlatformEnum(Enum):
    WEB = "web"
    ANDROID = "android"

FOTO_PROFILE_BASE_URL = os.getenv("USER_PROFILE_BASE_URL")
FOTO_PROFILE_BASE_STORE = os.getenv("USER_PROFILE_BASE_STORE")

async def register(auth : RegisterRequest,session : AsyncSession) -> UserBase:
    findUserByEmail = (await session.execute(select(User).where(User.email == auth.email))).scalar_one_or_none()

    if findUserByEmail :
        raise HttpException(400,"email already exists")
    
    userMapping = {"id" : generate_id(),"name" : auth.name,"email" : auth.email,"password" : create_hash_password(auth.password),"role" : UserRoleEnum.USER.value,"verified" : False}

    if auth.foto_profile :
        ext_file = auth.foto_profile.filename.split(".")

        if ext_file[-1] not in ["jpg","png","jpeg"] :
            raise HttpException(400,f"file harus berupa gambar")

        file_name = f"{generate_id()}-{auth.foto_profile.filename.split(' ')[0].split('.')[0]}.{ext_file[-1]}"
        file_name_save = f"{FOTO_PROFILE_BASE_STORE}{file_name}"

        async with aiofiles.open(file_name_save, "wb") as f:
            await f.write(auth.foto_profile.file.read())
            userMapping["foto_profile"] = f"{FOTO_PROFILE_BASE_URL}/{file_name}"
    
    session.add(User(**userMapping))

    # send otp for verify email
    otpCode = random_strings.random_digits(6)

    otpMapping = {"id" : generate_id(),"user_id" : userMapping["id"],"otp" : otpCode,"expires_at" : datetime.now() + timedelta(minutes=5)}
    session.add(OtpCode(**otpMapping))
    await session.commit()
    await sendOtp(auth.email,"Verify Account","Verify Account With OTP",otpCode)

    return {
        "msg" : "register success",
        "data" : {
            "id" : userMapping["id"],
            "name" : userMapping["name"],
            "email" : userMapping["email"],
            "role" : userMapping["role"],
            "verified" : userMapping["verified"]
        }
    }

async def verify_account(id : int,otp : str,session : AsyncSession) -> bool :
    findUser = (await session.execute(select(User).where(User.id == id))).scalar_one_or_none()

    if not findUser :
        raise HttpException(status=400,message="user not found")  
    
    findOtpUser = (await session.execute(select(OtpCode).where(OtpCode.user_id == findUser.id).order_by(OtpCode.expires_at.desc()))).scalars().all()

    if len(findOtpUser) == 0 :
        raise HttpException(400,"otp invalid")
    
    if datetime.now() > findOtpUser[0].expires_at :
        await session.delete(findOtpUser[0])
        await session.commit()
        raise HttpException(400,"token expires")
    if findOtpUser[0].otp != otp :
        raise HttpException(400,"otp invalid")
    
    findUser.verified = True
    await session.commit()
    return {
        "msg" : "verify account success"
    }

ANDROID_GOOGLE_CLIENT_ID = os.getenv("ANDROID_GOOGLE_CLIENT_ID")
WEB_GOOGLE_CLIENT_ID = os.getenv("WEB_GOOGLE_CLIENT_ID")
async def registerWithOauth2(token_google_id : str,platform : PlatformEnum,session : AsyncSession) -> UserBase:
    request = requests.Request()

    try :
        print(ANDROID_GOOGLE_CLIENT_ID)
        print(token_google_id)
        id_info = id_token.verify_oauth2_token(
            token_google_id, request, ANDROID_GOOGLE_CLIENT_ID if platform == PlatformEnum.ANDROID else WEB_GOOGLE_CLIENT_ID)
        
        if id_info['iss'] != 'https://accounts.google.com':
            raise HttpException('Wrong issuer.')
        
        userEmail = id_info["email"]
        findUserByEmail = (await session.execute(select(User).where(User.email == userEmail))).scalar_one_or_none()

        if findUserByEmail :
            raise HttpException(400,"akun telah ditambahkan")

        userMapping = {"id" : generate_id(),"name" : id_info["given_name"],"email" : userEmail,"password" : None,"role" : UserRoleEnum.USER.value,"verified" : True}
        session.add(User(**userMapping))
        await session.commit()

        return {
            "msg" : "register success",
            "data" : {
                "id" : userMapping["id"],
                "name" : userMapping["name"],
                "email" : userMapping["email"],
                "role" : userMapping["role"],
                "verified" : userMapping["verified"]
                }
        }
    except Exception as err :
        raise HttpException(400,f"something wrong {err.args[0]}")

async def loginWithOauth2(token_google_id : str,Res : Response,platform : PlatformEnum,session : AsyncSession) -> LoginOauth2Response:
    request = requests.Request()

    try :
        id_info = id_token.verify_oauth2_token(
            token_google_id, request, ANDROID_GOOGLE_CLIENT_ID if platform == PlatformEnum.ANDROID else WEB_GOOGLE_CLIENT_ID)
        
        if id_info['iss'] != 'https://accounts.google.com':
            raise HttpException('Wrong issuer.')
        
        userEmail = id_info["email"]
        findUserByEmail = (await session.execute(select(User).where(User.email == userEmail))).scalar_one_or_none()

        if not findUserByEmail :
            raise HttpException(400,"akun tidak ditemukan")

        token_payload = {"id" : findUserByEmail.id}
        token = create_token(token_payload)
        Res.set_cookie("access_token",token["access_token"])
        Res.set_cookie("refresh_token",token["refresh_token"])

        return {
            "msg" : "login success",              
            "data" : {
                **token,
                "role" : findUserByEmail.role
            }
        }  
    except Exception as err :
        raise HttpException(400,f"something wrong {err.args[0]}")

async def adminAndSuperAdminLogin(auth : LoginRequest,Res : Response,session : AsyncSession) -> LoginResponse :
    findUser = (await session.execute(select(User).where(and_(User.email == auth.email,or_(User.role == UserRoleEnum.ADMIN.value,User.role == UserRoleEnum.SUPER_ADMIN.value))))).scalar_one_or_none()

    if not findUser :
        raise HttpException(status=400,message="email atau password salah")
    
    if findUser.role == UserRoleEnum.SUPER_ADMIN :
        isPassword = auth.password == findUser.password
    else :
        isPassword = verify_hash_password(auth.password,findUser.password)

    if not isPassword :
        raise HttpException(status=400,message="email atau password salah")
    
    token_payload = {"id" : findUser.id}

    token = create_token(token_payload)
    Res.set_cookie("access_token",token["access_token"])
    Res.set_cookie("refresh_token",token["refresh_token"])

    return {
        "msg" : "login success",              
        "data" : {
            **token,
            "role" : findUser.role
        }
    }  


async def userLogin(auth : LoginRequest,Res : Response,session : AsyncSession) -> LoginResponse :
    findUser = (await session.execute(select(User).where(and_(User.email == auth.email,User.role == UserRoleEnum.USER.value)))).scalar_one_or_none()

    if not findUser :
        raise HttpException(status=400,message="email atau password salah")
    
    if not findUser.verified :
        raise HttpException(401,"user not verified")
    
    isPassword = verify_hash_password(auth.password,findUser.password)
    if not isPassword :
        raise HttpException(status=400,message="email atau password salah")

    token_payload = {"id" : findUser.id}

    token = create_token(token_payload)
    Res.set_cookie("access_token",token["access_token"])
    Res.set_cookie("refresh_token",token["refresh_token"])

    return {
        "msg" : "login success",              
        "data" : {
            **token,
        }
    }
        
    
async def refresh_token(data,Res : Response) -> RefreshTokenResponse :
    token_payload = {"id" : data["id"]}

    token = create_token(token_payload)
    Res.set_cookie("access_token",token["access_token"],httponly=True,max_age="24 * 60 * 60 * 60")
    Res.set_cookie("refresh_token",token["refresh_token"],httponly=True,max_age="24 * 60 * 60 * 60 * 60")
    return {
        "msg" : "succes",
        "data" : token
    }

#logout
async def logout(Res : Response) :
    Res.delete_cookie("access_token")
    Res.delete_cookie("refresh_token")
    return {
        "msg" : "logout success"
    }

async def cekAkunAndSendOtp(email : str,session : AsyncSession) -> ForgotPasswordResponse :
    findUser = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()

    if not findUser :
        raise HttpException(status=400,message="akun tidak ditemukan")
    
    otpCode = random_strings.random_digits(6)

    otpMapping = {"id" : generate_id(),"user_id" : findUser.id,"otp" : otpCode,"expires_at" : datetime.now() + timedelta(minutes=5)}
    await session.execute(text('DELETE FROM otp where user_id = :user_id'),{"user_id" : findUser.id})
    session.add(OtpCode(**otpMapping))
    await session.commit()
    await session.refresh(findUser)
    await sendOtp(email,"Verify Account","Verify Account With OTP",otpCode)
    return {       
        "msg" : "OTP berhasil dikirim",   
        "data" : {
            "id" : findUser.id,
            "email" : findUser.email
        }
    }
    
    

async def check_otp(email : str,otp : str,session : AsyncSession) -> bool :
    findUser = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()

    if not findUser :
        raise HttpException(status=400,message="otp is not valid")  
    
    findOtpUser = (await session.execute(select(OtpCode).where(OtpCode.user_id == findUser.id).order_by(OtpCode.expires_at.desc()))).scalars().all()

    print(findOtpUser)
    if len(findOtpUser) == 0 :
        raise HttpException(400,"otp invalid")
    
    if datetime.now() > findOtpUser[0].expires_at :
        await session.delete(findOtpUser)
        await session.commit()
        raise HttpException(400,"token expires")
    if findOtpUser[0].otp != otp :
        raise HttpException(400,"otp invalid")
    
    return {
        "msg" : "Validation success, otp is valid"
    }       
         

async def send_otp_again(email : int,session : AsyncSession) :
        findUser = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()

        if not findUser :
            raise HttpException(status=400,message="akun tidak ditemukan")
        
        otpCode = random_strings.random_digits(6)
        otpMapping = {"id" : generate_id(),"user_id" : findUser.id,"otp" : otpCode,"expires_at" : datetime.now() + timedelta(minutes=5)}
        await session.execute(text('DELETE FROM otp where user_id = :user_id'),{"user_id" : findUser.id})
        session.add(OtpCode(**otpMapping))
        await session.commit()
        await sendOtp(email,"Verify Account","Verify Account With OTP",otpCode)

        return {
            "msg" : "send message success"
        }
        
    

async def update_password(email : int,password : str,otp : int,session : AsyncSession) :
    findUser = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()

    if not findUser :
        raise HttpException(status=400,message="akun tidak ditemukan")
    
    findOtpUser = (await session.execute(select(OtpCode).where(OtpCode.user_id == findUser.id).order_by(OtpCode.expires_at.desc()))).scalars().all()

    if not findOtpUser :
        raise HttpException(400,"otp invalid")
    
    if findOtpUser[0].otp != otp :
        raise HttpException(400,"otp invalid")
    
    if findUser.role == UserRoleEnum.ADMIN :
        findUser.password = password
    else :
        findUser.password = create_hash_password(password)
    await session.commit()

    return {
        "msg" : "update password success"
    }
            
          
    

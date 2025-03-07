from pydantic import BaseModel, EmailStr
from fastapi import Form,UploadFile,File
from ..schemas.passwordValidation_schema import PasswordValidation
from ...types.user_types import UserRoleEnum


class RegisterRequest(PasswordValidation) :
    name : str
    email : EmailStr
    password : str
    foto_profile : UploadFile | None = None
    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            email: EmailStr = Form(...),
            password: str = Form(...),
            foto_profile: UploadFile | None = File(None)
        ):
            return cls(
                name=name,
                email=email,
                foto_profile=foto_profile,
                password=password
            )

class VerifyAccountRequest(BaseModel) :
    id : int
    otp : int

class Oauth2Request(BaseModel) :
    token_google_id : str

class LoginRequest(PasswordValidation) :
    email : EmailStr
    password : str

class LoginResponse(BaseModel) :
    access_token : str
    refresh_token : str
    role : UserRoleEnum | None = None

class LoginOauth2Response(BaseModel) :
    access_token : str
    refresh_token : str
    role : UserRoleEnum

class RefreshTokenResponse(BaseModel) :
    access_token : str
    refresh_token : str

class ForgotPasswordResponse(BaseModel) :
    id : int
    email : EmailStr
    
class ForgotPasswordIdentifyRequest(BaseModel) :
    email : EmailStr

class SendOtpAgainRequest(BaseModel) :
    email : EmailStr

class ValidationOTPRequest(BaseModel) :
    email : EmailStr
    otp : int

class UpdatePasswordRequest(BaseModel) :
    email : EmailStr
    OTP : int
    password : str
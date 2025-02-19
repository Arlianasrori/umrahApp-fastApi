from pydantic import BaseModel, EmailStr
from ..schemas.passwordValidation_schema import PasswordValidation
from ...types.user_types import UserRoleEnum

class RegisterRequest(PasswordValidation) :
    name : str
    email : EmailStr
    password : str

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
from fastapi import APIRouter,Depends, Request,Response

# model and service
from ..domain.auth import authService
from ..domain.auth.authSchema import LoginRequest,ForgotPasswordResponse,ForgotPasswordIdentifyRequest,SendOtpAgainRequest,UpdatePasswordRequest,LoginResponse,RefreshTokenResponse,ValidationOTPRequest,RegisterRequest,VerifyAccountRequest,Oauth2Request,LoginOauth2Response
from ..db.sessionDepedency import sessionDepedency

# schema
from ..domain.auth.authSchema import RegisterRequest
from ..domain.schemas.user_schema import UserBase
from ..domain.schemas.response_schema import ApiResponse,MessageOnlyResponse
from ..types.user_types import UserRoleEnum

# depends
from ..auth.auth_depends.admin.depend_refresh_auth_admin import adminrefreshAuth
from ..auth.auth_depends.user.depend_refresh_auth_user import userrefreshAuth


authRouter = APIRouter(prefix="/auth")

@authRouter.post("/register",response_model=ApiResponse[UserBase],tags=["AUTH/REGISTER"])
async def register(auth : RegisterRequest = Depends(RegisterRequest.as_form),session : sessionDepedency = None) :
    return await authService.register(auth,session)

@authRouter.post("/register/verify",response_model=ApiResponse[UserBase],tags=["AUTH/REGISTER"])
async def register_verify(auth : VerifyAccountRequest,session : sessionDepedency) :
    return await authService.verify_account(auth.id,auth.otp,session)

@authRouter.post("/register/oauth2",response_model=ApiResponse[UserBase],tags=["AUTH/REGISTER"])
async def register_oauth2(auth : Oauth2Request,platform : authService.PlatformEnum,session : sessionDepedency) :
    return await authService.registerWithOauth2(auth.token_google_id,platform,session)

# admin  auth
@authRouter.post("/admin/login",response_model=ApiResponse[LoginResponse],tags=["AUTH/ADMIN"])
async def admin_login(auth : LoginRequest,Res : Response,session : sessionDepedency) :
    return await authService.adminLogin(auth,Res,session)

@authRouter.post("/admin/refreshToken",dependencies=[Depends(adminrefreshAuth)],response_model=ApiResponse[RefreshTokenResponse],tags=["AUTH/ADMIN"])
async def admin_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token(Req.admin,UserRoleEnum.ADMIN,Res)

# user auth
@authRouter.post("/user/login",response_model=ApiResponse[LoginResponse],tags=["AUTH/USER"])
async def user_login(auth : LoginRequest,Res : Response,session : sessionDepedency) :
    return await authService.userLogin(auth,Res,session)

@authRouter.post("/user/refreshToken",dependencies=[Depends(userrefreshAuth)],response_model=ApiResponse[RefreshTokenResponse],tags=["AUTH/USER"])
async def user_refresh_token(Req : Request,Res : Response) :
    return await authService.refresh_token(Req.siswa,UserRoleEnum.SISWA,Res)

# all logout
@authRouter.post("/login/oauth2",response_model=ApiResponse[LoginOauth2Response],tags=["AUTH/REGISTER"])
async def login_oauth2(auth : Oauth2Request,platform : authService.PlatformEnum,Res : Response,session : sessionDepedency) :
    return await authService.loginWithOauth2(auth.token_google_id,platform,Res,session)

@authRouter.post("/logout",tags=["AUTH"])
async def logout(Res : Response) :
    return await authService.logout(Res)

# reset password
@authRouter.post("/checkAccountAndSendOtp",response_model=ApiResponse[ForgotPasswordResponse],tags=["AUTH/RESET_PASSWORD"])
async def cek_akun_and_send_otp(data : ForgotPasswordIdentifyRequest,session : sessionDepedency = None) :
    return await authService.cekAkunAndSendOtp(data.email,session)

@authRouter.post("/sendOTPAgain",response_model=MessageOnlyResponse,tags=["AUTH/RESET_PASSWORD"])
async def sendUlangOTP(body : SendOtpAgainRequest,session : sessionDepedency) :
    return await authService.send_otp_again(body.email,session)

@authRouter.post("/validationOTP",response_model=MessageOnlyResponse,tags=["AUTH/RESET_PASSWORD"])
async def validationOTP(body : ValidationOTPRequest,session : sessionDepedency) :
    return await authService.check_otp(body.email,body.otp,session)

@authRouter.patch("/updatePassword",response_model=MessageOnlyResponse,tags=["AUTH/RESET_PASSWORD"])
async def update_password(body : UpdatePasswordRequest,session : sessionDepedency) :
    return await authService.update_password(body.email,body.password,body.OTP,session)


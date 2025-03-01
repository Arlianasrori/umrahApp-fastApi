from pydantic import  EmailStr
from fastapi import Form,UploadFile,File
from ..schemas.passwordValidation_schema import PasswordValidation

class AddAdminRequest(PasswordValidation) :
    name : str
    email : EmailStr
    password : str
    foto_profile : UploadFile | None = None

    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            email: EmailStr = Form(...),
            foto_profile: UploadFile = File(...),
            password: str = Form(...),
        ):
            return cls(
                name=name,
                email=email,
                foto_profile=foto_profile,
                password=password,
            )
    
class UpdateAdminRequest(PasswordValidation) :
    name : str | None = None
    email : EmailStr = None
    password : str | None = None
    foto_profile : UploadFile | None = None

    @classmethod
    def as_form(
            cls,
            name: str | None = Form(...),
            email: EmailStr | None= Form(...),
            foto_profile: UploadFile | None = File(...),
            password: str | None= Form(...),
        ):
            return cls(
                name=name,
                email=email,
                foto_profile=foto_profile,
                password=password,
            )
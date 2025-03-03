from pydantic import BaseModel, EmailStr, field_validator
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
            foto_profile: UploadFile = File(None),
            password: str = Form(...),
        ):
            return cls(
                name=name,
                email=email,
                foto_profile=foto_profile,
                password=password,
            )
    
class UpdateAdminRequest(BaseModel) :
    name : str | None = None
    email : EmailStr | None = None
    password : str | None = None
    foto_profile : UploadFile | None = None

    @field_validator('password')
    def validate_password(cls, v):
        print("tes")
        if v is None :
            return None
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        elif " " in v :
            raise ValueError("Password tidak boleh mengandung spasi")
        elif not any(char.isdigit() for char in v) :
            raise ValueError("Password harus mengandung angka")
        elif not any(char.isalpha() for char in v) :
            raise ValueError("Password harus mengandung huruf huruf")
        return v

    @classmethod
    def as_form(
            cls,
            name: str | None = Form(None),
            email: EmailStr | None= Form(None),
            foto_profile: UploadFile | None = File(None),
            password: str | None= Form(None),
        ):
            return cls(
                name=name,
                email=email,
                foto_profile=foto_profile,
                password=password,
            )
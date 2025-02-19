from pydantic import BaseModel,field_validator

class PasswordValidation(BaseModel) :
    password : str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        elif " " in v :
            raise ValueError("Password tidak boleh mengandung spasi")
        elif not any(char.isdigit() for char in v) :
            raise ValueError("Password harus mengandung angka")
        elif not any(char.isalpha() for char in v) :
            raise ValueError("Password harus mengandung huruf huruf")
        return v
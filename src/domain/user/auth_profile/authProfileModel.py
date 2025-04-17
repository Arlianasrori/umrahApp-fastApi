from pydantic import BaseModel
from fastapi import Form,UploadFile,File

class UpdateProfileRequest(BaseModel) :
    name : str | None 
    fcm_token : str | None
    foto_profile : UploadFile | None
    @classmethod
    def as_form(
            cls,
            name: str | None = Form(None),
            fcm_token: str | None = Form(None),
            foto_profile: UploadFile | None = File(None), 
        ):
            return cls(
                name=name,
                fcm_token=fcm_token,
                foto_profile=foto_profile
            )
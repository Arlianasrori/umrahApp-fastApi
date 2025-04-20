from pydantic import BaseModel
from fastapi import Form, UploadFile, File
from typing import Optional

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None  # Gunakan Optional[str] atau str | None
    fcm_token: Optional[str] = None
    foto_profile: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),  # Pastikan Form(None) untuk opsional
        fcm_token: Optional[str] = Form(None),
        foto_profile: Optional[UploadFile] = File(None),  # File(None) untuk opsional
    ):
        return cls(
            name=name,
            fcm_token=fcm_token,
            foto_profile=foto_profile
        )

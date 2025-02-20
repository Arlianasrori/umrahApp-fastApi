from pydantic import BaseModel

class UserBase(BaseModel) :
    id : int
    name : str
    email : str
    role : str
    foto_profile : str | None = None
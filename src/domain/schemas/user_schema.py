from pydantic import BaseModel

class UserBase(BaseModel) :
    id : int
    name : str
    email : str
    role : str
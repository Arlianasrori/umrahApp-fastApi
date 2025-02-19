from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    msg : str
    data: T

class MessageOnlyResponse(BaseModel) :
    msg : str
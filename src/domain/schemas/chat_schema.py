from pydantic import BaseModel
from datetime import datetime
from ..schemas.package_schema import PackageBase
from ..schemas.user_schema import UserBase

class MediaMessageBase(BaseModel) :
    id : int
    type : str
    url : str

class MessageBase(BaseModel) :
    id : int 
    room_id : int
    message : str
    is_read : bool
    created_at : datetime
    updated_at : datetime
    package : PackageBase | None = None
    media : list[MediaMessageBase] | None = None 

class MessageWithSenderReceiver(MessageBase) :
    receiver : UserBase
    sender : UserBase

class RoomUserBase(BaseModel) :
    id : int
    deleted : bool
    user : UserBase

class RoomBase(BaseModel) :
    id : int
    created_at : datetime
    updated_at : datetime
    messages : list[MessageBase] | None = None
    roomUser : list[RoomUserBase] | None = None
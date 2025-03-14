from pydantic import BaseModel
from datetime import datetime

class AddMessageRequest(BaseModel) :
    receiver_id : int
    package_id : int | None = None
    message : str

class UpdateMessageRequest(BaseModel) :
    message : str 

class GetRoomQuery(BaseModel) :
    receiver_name : str | None = None

class GetRoomResponse(BaseModel) :
    room_id : int
    to_user_name : str
    to_user_id : int
    last_message : str
    last_message_time : datetime
    count_not_read_message : int
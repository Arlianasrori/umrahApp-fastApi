from pydantic import BaseModel

class AddMessageRequest(BaseModel) :
    receiver_id : int
    message : str

class UpdateMessageRequest(BaseModel) :
    message : str 

class GetRoomQuery(BaseModel) :
    receiver_name : str | None = None
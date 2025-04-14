from pydantic import BaseModel
from ...utils.generateId_util import generate_id
from enum import Enum

class AddNotificationRequest(BaseModel):
    id : int = generate_id()
    user_id : int
    title : str
    body : str

class FCMType(Enum) :
    notification = "notification"
    chat = "chat"

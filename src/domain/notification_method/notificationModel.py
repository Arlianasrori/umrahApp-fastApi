from pydantic import BaseModel
from ...utils.generateId_util import generate_id
from enum import Enum
from ...types.notification_types import NotificationDataEnum

class AddNotificationRequest(BaseModel):
    id : int = generate_id()
    user_id : int
    title : str
    body : str
    data_id : int | None = None
    data_type : NotificationDataEnum | None = None

class FCMType(Enum) :
    notification = "notification"
    chat_room = "chat_room"
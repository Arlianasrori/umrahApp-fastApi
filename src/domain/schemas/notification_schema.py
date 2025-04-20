from pydantic import BaseModel
from datetime import datetime, date
from ...types.notification_types import NotificationDataEnum 

class NotificationReadBase(BaseModel):
    id : int
    is_read : bool

class NotificationDataBase(BaseModel) :
    id : int
    notification_id : int
    data_id : int
    data_type : NotificationDataEnum

class NotificationBase(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    reads : list[NotificationReadBase] = []
    data : NotificationDataBase | None = None

class ResponseGetUnreadNotification(BaseModel):
    count : int
from pydantic import BaseModel
from datetime import datetime, date

class NotificationReadModelBase(BaseModel):
    id : int
    is_read : bool

class NotificationModelBase(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    reads : list[NotificationReadModelBase] = []

# class ResponseGetAllNotification(BaseModel):
#     msg : str
#     data : dict[date,list[NotificationModelBase]]

class ResponseGetUnreadNotification(BaseModel):
    count : int
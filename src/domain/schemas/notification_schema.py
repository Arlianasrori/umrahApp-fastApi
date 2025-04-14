from pydantic import BaseModel
from datetime import datetime, date

class NotificationReadBase(BaseModel):
    id : int
    is_read : bool

class NotificationBase(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    reads : list[NotificationReadBase] = []

class ResponseGetUnreadNotification(BaseModel):
    count : int
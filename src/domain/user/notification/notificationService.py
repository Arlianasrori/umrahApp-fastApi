from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,not_
from sqlalchemy.orm import subqueryload

# models
from ....models.notification_model import Notification,NotificationRead
# schemas
from ...schemas.notification_schema import NotificationBase,ResponseGetUnreadNotification
# common
from ....error.errorHandling import HttpException
from collections import defaultdict
from ....utils.generateId_util import generate_id
from datetime import date

async def getAllNotification(user_id : int,session : AsyncSession) -> dict[date,list[NotificationBase]] :
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.user_id == user_id))).where(Notification.user_id == user_id).order_by(desc(Notification.created_at)))).scalars().all()

    grouped_notifications = defaultdict(list)
    for notification in findNotification:
        grouped_notifications[notification.created_at.date()].append(notification)

    return {
        "msg" : "success",
        "data" : grouped_notifications
    }

async def getNotificationById(id_notification : int,user_id : int,session : AsyncSession) -> NotificationBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.user == user_id))).where(and_(Notification.id == id_notification,Notification.user_id == user_id)))).scalar_one_or_none()

    if not findNotification :
        raise HttpException(400,"notification is not found")
    
    return {
        "msg" : "success",
        "data" : findNotification
    }

async def readNotification(id_notification : int,user_id : int,session : AsyncSession) -> NotificationBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.user_id == user_id))).where(and_(Notification.id == id_notification,Notification.user_id == user_id)))).scalar_one_or_none()

    if not findNotification :
        raise HttpException(400,"notification is not found")
    
    if len(findNotification.reads) > 0 :
        raise HttpException(400,"notification has been read")
    
    notificationMapping = {
        "id" : generate_id(),
        "notification_id" : id_notification,
        "user_id" : user_id,
        "is_read" : True
    }

    notifDictCopy = deepcopy(findNotification.__dict__)
    session.add(NotificationRead(**notificationMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : {
            **notifDictCopy,
            "reads" : [notificationMapping]
        }
    }

async def getCountNotification(user_id : int,session : AsyncSession) -> ResponseGetUnreadNotification:
    findNotification = (await session.execute(select(Notification).where(and_(Notification.user_id == user_id,not_(Notification.reads.any(NotificationRead.user_id == user_id)))))).scalars().all()

    return {
        "msg" : "success",
        "data" : {
            "count" : len(findNotification)
        }
    }

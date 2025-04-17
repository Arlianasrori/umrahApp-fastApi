from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,desc, select,and_,not_,text,or_
from sqlalchemy.orm import subqueryload,joinedload

# models
from ...models.notification_model import Notification
from .notificationModel import AddNotificationRequest, FCMType
from ...models.user_model import User
from ...models.notification_model import Notification,NotificationRead, NotificationData
from ...models.package_model import Package

# schemas
from ..schemas.notification_schema import NotificationBase,ResponseGetUnreadNotification
# types
from ...types.notification_types import NotificationDataEnum

# common
from ...error.errorHandling import HttpException
from ...db.db import SessionLocal
from collections import defaultdict
from datetime import date
from ...utils.generateId_util import generate_id
import os
import asyncio
from multiprocessing import Process
from copy import deepcopy

from ...socket.socket_connection_handling import sio,getUserSid

# FCM
import firebase_admin
from firebase_admin import credentials, messaging


# Inisialisasi SDK dengan file kunci layanan Anda
cred = credentials.Certificate(f"{os.getcwd()}/{os.getenv("FCM_PATH_KEY")}")
firebase_admin.initialize_app(cred)

async def addNotification(data : AddNotificationRequest) -> None:
    async with SessionLocal() as session :
        try :
            data = AddNotificationRequest(**data)

            findUser = (await session.execute(select(User).where(User.id == data.user_id))).scalar_one_or_none()

            if not findUser :
                raise HttpException(400,"user tidak ditemukan")

            session.add(Notification(**data.model_dump(exclude={"data_id","data_type"})))
            if data.data_id :
                if data.data_type == NotificationDataEnum.package :
                    findPackage = (await session.execute(select(Package).where(Package.id == data.data_id))).scalar_one_or_none()

                    if not findPackage :
                        return
                
                notificationDataMapping = {"id" : generate_id(),"notification_id" : data.id,"data_id" : data.data_id,"data_type" : data.data_type}
                session.add(NotificationData(**notificationDataMapping))

            userDictCopy = deepcopy(findUser.__dict__)
            await session.commit()
            await session.reset()

            user_sid = await getUserSid(data.user_id)
            if user_sid :
                await sio.emit("new_notification",data.model_dump(),user_sid)

            # send notificatio to user using firebase cloud messaging
            if userDictCopy["fcm_token"] and id :
                await kirim_pesan_fcm(userDictCopy["fcm_token"], data.title, data.body,userDictCopy["id"],data.id,FCMType.notification)

        except Exception as e:
            print(f"Terjadi kesalahan: pada notificationService.py {e}")
        finally :
            await session.close()
 

async def resetTokenFCM(id_user : int,session : AsyncSession):
    findUser = (await session.execute(select(User).where(User.id == id_user))).scalar_one_or_none()

    if findUser :
        findUser.fcm_token = None
        await session.commit()

async def kirim_pesan_fcm(token_FCM : str, title : str, body : str,id_user : int,id_type : int,type : FCMType):
    try:
        session = SessionLocal()
        if token_FCM :
            pesan = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={
                    "id" : id_type,
                    "type" : type.value
                },
                token=token_FCM,
            )
            response = messaging.send(pesan)
            print(f"Pesan berhasil dikirim: {response}")
            
    except Exception as e:
        # jika ada kesalahan pada token fcmUser maka akan dihapus dan dapat diupdate kembali
        await resetTokenFCM(id_user , session)
        print(f"Terjadi kesalahan: {e}")
    finally :
        await session.close()

# using for send notif async
def sendNotificationAsync(body : AddNotificationRequest) :
    asyncio.run(addNotification(body))

# using send notification  with diffrent thread
def sendNotificationThreadProccess(body : AddNotificationRequest) :
    process = Process(target=sendNotificationAsync,args=(body,))
    process.start()


# get notification
async def getAllNotification(user_id : int,session : AsyncSession) -> dict[date,list[NotificationBase]] :
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.user_id == user_id)),joinedload(Notification.data)).where(Notification.user_id == user_id).order_by(desc(Notification.created_at)))).scalars().all()

    grouped_notifications = defaultdict(list)
    for notification in findNotification:
        grouped_notifications[notification.created_at.date()].append(notification)

    return {
        "msg" : "success",
        "data" : grouped_notifications
    }

async def getNotificationById(id_notification : int,user_id : int,session : AsyncSession) -> NotificationBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.user_id == user_id)),joinedload(Notification.data)).where(and_(Notification.id == id_notification,Notification.user_id == user_id)))).scalar_one_or_none()

    if not findNotification :
        raise HttpException(400,"notification is not found")
    
    return {
        "msg" : "success",
        "data" : findNotification
    }

async def readNotification(id_notification : int,user_id : int,session : AsyncSession) -> NotificationBase:
    findNotification = (await session.execute(select(Notification).options(subqueryload(Notification.reads.and_(NotificationRead.user_id == user_id)),joinedload(Notification.data)).where(and_(Notification.id == id_notification,Notification.user_id == user_id)))).scalar_one_or_none()

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

async def readAllNotif(user_id : int,session : AsyncSession) :
    findAllNotif = (await session.execute(select(Notification).where(~Notification.reads.any(NotificationRead.user_id == user_id),or_(Notification.user_id == user_id,Notification.user_id == None)))).scalars().all()

    notifReadDataDb = []
    for notif in findAllNotif :
        notifReadDataDb.append(NotificationRead(**{"id" : generate_id(),"user_id" : user_id,"notification_id" : notif.id,"is_read" : True}))
    
    if len(notifReadDataDb) != 0 :
        session.add_all(notifReadDataDb)

    await session.commit()

    return {
        "msg" : "read all notif success"
    }
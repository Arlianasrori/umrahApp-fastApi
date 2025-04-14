from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# models
from ...models.notification_model import Notification
from .notificationModel import AddNotificationRequest, FCMType
from ...models.user_model import User
from ...models.notification_model import Notification,NotificationRead

# schemas
from ..schemas.notification_schema import NotificationBase,ResponseGetUnreadNotification

# common
from ...error.errorHandling import HttpException
from ...db.db import SessionLocal
from collections import defaultdict
from datetime import date
from ...utils.generateId_util import generate_id

# FCM
import firebase_admin
from firebase_admin import credentials, messaging
import os
import asyncio
from multiprocessing import Process
from copy import deepcopy

from copy import deepcopy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, select,and_,not_
from sqlalchemy.orm import subqueryload


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
                
            session.add(Notification(**data.model_dump()))

            userDictCopy = deepcopy(findUser.__dict__)
            await session.commit()
            await session.reset()

            # send notificatio to user using firebase cloud messaging
            if userDictCopy["fcm_token"] and id :
                await kirim_pesan_fcm(userDictCopy["fcm_token"], data.title, data.body,userDictCopy["id"],data.id)
        except Exception as e:
            print(f"Terjadi kesalahan: pada notificationService.py {e}")
        finally :
            await session.close()
 

async def resetTokenFCM(id_user : int,session : AsyncSession):
    findUser = (await session.execute(select(User).where(User.id == id_user))).scalar_one_or_none()

    if findUser :
        findUser.fcm_token = None
        await session.commit()

async def kirim_pesan_fcm(token_FCM : str, title : str, body : str,id_user : int,notification_id : int):
    try:
        session = SessionLocal()
        if token_FCM :
            pesan = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={
                    "id" : notification_id,
                    "type" : FCMType.notification
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

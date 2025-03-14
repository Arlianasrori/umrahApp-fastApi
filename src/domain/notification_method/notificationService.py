from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# models
from ...models.notification_model import Notification
from .notificationModel import AddNotificationModel
from ...models.user_model import User

# common
from ...error.errorHandling import HttpException
from ...db.db import SessionLocal

# FCM
import firebase_admin
from firebase_admin import credentials, messaging
import os
import asyncio
from multiprocessing import Process
from copy import deepcopy
from ...socket.socket_connection_handling import sio,getUserSid

# Inisialisasi SDK dengan file kunci layanan Anda
cred = credentials.Certificate(f"{os.getcwd()}/{os.getenv("FCM_PATH_KEY")}")
firebase_admin.initialize_app(cred)

async def addNotification(data : AddNotificationModel) -> None:
    async with SessionLocal() as session :
        try :
            data = AddNotificationModel(**data)

            findUser = (await session.execute(select(User).where(User.id == data.user_id))).scalar_one_or_none()

            if not findUser :
                raise HttpException(400,"user tidak ditemukan")
                
            session.add(Notification(**data.model_dump()))

            userDictCopy = deepcopy(findUser.__dict__)
            await session.commit()
            await session.reset()

            user_sid = await getUserSid(data.user_id)
            if user_sid :
                await sio.emit("new_notification",data.model_dump(),user_sid)

            # send notificatio to user using firebase cloud messaging
            if userDictCopy["fcm_token"] and id :
                await kirim_pesan_fcm(userDictCopy["fcm_token"], data.title, data.body,userDictCopy["id"])
        except Exception as e:
            print(f"Terjadi kesalahan: pada notificationService.py {e}")
        finally :
            await session.close()
 

async def resetTokenFCM(id_user : int,session : AsyncSession):
    findUser = (await session.execute(select(User).where(User.id == id_user))).scalar_one_or_none()

    if findUser :
        findUser.fcm_token = None
        await session.commit()

async def kirim_pesan_fcm(token_FCM : str, title : str, body : str,id_user : int):
    try:
        session = SessionLocal()
        if token_FCM :
            pesan = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
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

# using for send notif using multiprocessing
def sendNotificationProccesSync(body : AddNotificationModel) :
    asyncio.run(addNotification(body))

# using send notification  with diffrent thread
def sendNotificationThreadProccess(body : AddNotificationModel) :
    process = Process(target=sendNotificationProccesSync,args=(body,))
    process.start()
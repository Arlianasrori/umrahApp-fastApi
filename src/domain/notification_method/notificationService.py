from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# models
from ...models.notification_model import Notification
from .notificationModel import AddNotificationModel
from ...models.siswa_model import Siswa
from ...models.guru_mapel_model import GuruMapel
from ...models.guru_walas_model import GuruWalas
from ...models.petugas_BK_model import PetugasBK

# common
from ...error.errorHandling import HttpException
from enum import Enum
from ...db.db import SessionLocal

# FCM
import firebase_admin
from firebase_admin import credentials, messaging
import os
import asyncio

# Inisialisasi SDK dengan file kunci layanan Anda
cred = credentials.Certificate(f"{os.getcwd()}/{os.getenv("FCM_PATH_KEY")}")
firebase_admin.initialize_app(cred)

class UserType(Enum):
    SISWA = "siswa"
    GURU_WALAS = "guru_walas"
    GURU_MAPEL = "guru_mapel"
    PETUGAS_BK = "petugas_BK"

async def addNotification(data : AddNotificationModel) -> None:
    async with SessionLocal() as session :
        try :
            data = AddNotificationModel(**data)
            token_FCM = None
            id = None
            userType : UserType = None

            if data.id_siswa :
                findSiswa = (await session.execute(select(Siswa).where(Siswa.id == data.id_siswa))).scalar_one_or_none()
                print(findSiswa)

                if not findSiswa :
                    raise HttpException(400,"siswa tidak ditemukan")
                
                token_FCM = findSiswa.token_FCM
                id = findSiswa.id
                userType = UserType.SISWA

            elif data.id_guru_mapel:
                findGuruMapel = (await session.execute(select(GuruMapel).where(GuruMapel.id == data.id_guru_mapel))).scalar_one_or_none()

                if not findGuruMapel :
                    raise HttpException(400,"guru mapel tidak ditemukan")
                
                token_FCM = findGuruMapel.token_FCM
                id = findGuruMapel.id
                userType = UserType.GURU_MAPEL

            elif data.id_guru_walas:
                findGuruWalas = (await session.execute(select(GuruWalas).where(GuruWalas.id == data.id_guru_walas))).scalar_one_or_none()

                if not findGuruWalas :
                    raise HttpException(400,"guru walas tidak ditemukan")
                token_FCM = findGuruWalas.token_FCM
                id = findGuruWalas.id
                userType = UserType.GURU_WALAS

            elif data.id_petugas_BK:
                findPetugasBK = (await session.execute(select(PetugasBK).where(PetugasBK.id == data.id_petugas_BK))).scalar_one_or_none()

                if not findPetugasBK :
                    raise HttpException(400,"petugas BK tidak ditemukan")
                
            session.add(Notification(**data.model_dump()))

            await session.commit()
            await session.reset()

            # send notificatio to user using firebase cloud messaging
            if token_FCM and id :
                await kirim_pesan_fcm(token_FCM, data.title, data.body, userType, id)
        except Exception as e:
            print(f"Terjadi kesalahan: pada notificationService.py {e}")
        finally :
            await session.close()
 

async def resetTokenFCM(userType : UserType, id_user : int,session : AsyncSession):
    if userType == UserType.SISWA:
        findSiswa = (await session.execute(select(Siswa).where(Siswa.id == id_user))).scalar_one_or_none()

        if findSiswa :
            findSiswa.token_fcm = None
            await session.commit()
    elif userType == UserType.GURU_WALAS:
        findGuruWalas = (await session.execute(select(GuruWalas).where(GuruWalas.id == id_user))).scalar_one_or_none()

        if findGuruWalas :
            findGuruWalas.token_fcm = None
            await session.commit()
    elif userType == UserType.GURU_MAPEL:
        findGuruMapel = (await session.execute(select(GuruMapel).where(GuruMapel.id == id_user))).scalar_one_or_none()

        if findGuruMapel :
            findGuruMapel.token_fcm = None
            await session.commit()   
    elif userType == UserType.PETUGAS_BK:
        findPetugasBK = (await session.execute(select(PetugasBK).where(PetugasBK.id == id_user))).scalar_one_or_none()

        if findPetugasBK :
            findPetugasBK.token_fcm = None
            await session.commit()

async def kirim_pesan_fcm(token_FCM : str, title : str, body : str,userType : UserType, id_user : int):
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
        await resetTokenFCM(userType, id_user , session)
        print(f"Terjadi kesalahan: {e}")
    finally :
        await session.close()

# using for send notif using multiprocessing
def sendNotificationProccesSync(body : AddNotificationModel) :
    asyncio.run(addNotification(body))
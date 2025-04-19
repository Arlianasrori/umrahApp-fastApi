from ...db.db import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import func, select,and_,or_,text
from sqlalchemy.orm import joinedload, subqueryload, selectinload

from ...models.chat_model import Message, Room,RoomUsers
from ...models.user_model import User
from ...types.user_types import UserRoleEnum

from ...utils.generateId_util import generate_id
from datetime import datetime
from copy import deepcopy

AUTO_RESPONSES = {
    "apakah gvinum travel terpercaya?": (
        "Ya, Gvinum Travel adalah travel umroh yang terpercaya.\n"
        "Kami memiliki izin resmi dari Kementerian Agama, serta track record keberangkatan jamaah yang jelas dan transparan. "
        "Kepuasan dan kenyamanan jamaah adalah prioritas utama kami, dengan layanan yang jujur dan sesuai syariat."
    ),
    
    "apakah gvinum travel cepat?": (
        "Tentu, Gvinum Travel mengutamakan kecepatan dalam pelayanan.\n"
        "Mulai dari pendaftaran, pengurusan visa, hingga informasi keberangkatan, semua proses kami rancang seefisien mungkin tanpa mengurangi kualitas layanan. "
        "Karena kami tahu, waktu Anda sangat berharga."
    ),
    
    "apakah gvinum travel sigap?": (
        "Sangat sigap.\n"
        "Tim kami siap membantu jamaah 24 jam, mulai dari proses sebelum berangkat hingga ketika berada di tanah suci. "
        "Bila ada kendala atau pertanyaan, kami tanggapi dengan cepat dan solutif."
    ),
    
    "apakah gvinum travel ter-update?": (
        "Gvinum Travel selalu mengikuti perkembangan terbaru.\n"
        "Kami terus update informasi seputar kebijakan pemerintah Arab Saudi, teknologi check-in, hingga program-program umroh terbaru. "
        "Semua kami lakukan agar jamaah mendapat pengalaman terbaik dan paling relevan."
    )
}

def check_exisitng_room(room_list : list,sender_id : int,receiver_id : int) -> Room | None:
    for room in room_list :
        if len(room.roomUser) == 2 :
            isSameRoom=False
            for roomUser in room.roomUser :
                if roomUser.user_id == sender_id or roomUser.user_id == receiver_id :
                    isSameRoom = True
                else :
                    isSameRoom=False
                    break
            if isSameRoom :
                return room
            else :
                return None

async def create_room(first_user_id : int,second_user_id : int,session : AsyncSession) -> int :
    roomMapping = {"id" : generate_id(),"created_at" : datetime.utcnow(),"updated_at" : datetime.utcnow()}
    roomUsersDb = [RoomUsers(**{"id" : generate_id(),"user_id" : first_user_id,"room_id" : roomMapping["id"],"deleted" : False}),RoomUsers(**{"id" : generate_id(),"user_id" : second_user_id,"room_id" : roomMapping["id"],"deleted" : False})]

    session.add(Room(**roomMapping))
    session.add_all(roomUsersDb)

    return roomMapping["id"]

async def check_auto_reply(user_id : int,message : str,room_id : int | None,user_reply_id : int | None) :
    message_reply = AUTO_RESPONSES.get(message)

    if message_reply :
        async with SessionLocal() as session: 
            if room_id :
                messageMapping = {"id" : generate_id(),"room_id" : room_id,"message" : message_reply,"sender_id" : user_reply_id,"receiver_id" : user_id,"id_package" :None,"package_prices_id" : None, "is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow()}

                session.add(Message(**messageMapping))
                await session.commit()
                
            else :
                findAdmin = (await session.execute(select(User).where(User.role == UserRoleEnum.ADMIN).limit(1))).scalars().all()

                if len(findAdmin) != 0 :
                    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser)).where(Room.roomUser.any(or_(RoomUsers.user_id == user_id,RoomUsers.user_id == findAdmin[0].id))))).scalars().all()

                    # mencari room yang berisi user dengan user id == id pengirim dan user id == id penerima
                    roomExist = check_exisitng_room(findRoom,user_id,findAdmin[0].id)

                    if roomExist is None :
                        room_id = await create_room(user_id,findAdmin[0].id,session)

                        # roomForResponse = {**roomMapping}
                    else :
                        roomUser = list(filter(lambda roomuser: roomuser.user_id == user_id, roomExist.roomUser))[0]
                        if roomUser.deleted :
                            roomUser.deleted = False
                        
                        room_id = findRoom[0].id
                    
                    messageMapping = [Message(**{"id" : generate_id(),"room_id" : room_id,"message" : message,"sender_id" : user_id,"receiver_id" : findAdmin[0].id,"id_package" :None,"package_prices_id" : None, "is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow()}),
                    Message(**{"id" : generate_id(),"room_id" : room_id,"message" : message_reply,"sender_id" : findAdmin[0].id,"receiver_id" : user_id,"id_package" :None,"package_prices_id" : None, "is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow()})]

                    session.add_all(messageMapping)
                    response = deepcopy(messageMapping[0].__dict__)
                    await session.commit()

                    return response
    else :
        return None
                
                


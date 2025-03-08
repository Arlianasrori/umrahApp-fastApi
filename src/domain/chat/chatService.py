from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_,or_,text
from fastapi import UploadFile
from sqlalchemy.orm import joinedload, subqueryload, selectinload
# models
from ...models.user_model import User
from ...models.chat_model import RoomUsers,Room,Message,MediaMessage

# schemas
from .chatSchema import AddMessageRequest, UpdateMessageRequest, GetRoomQuery, GetRoomResponse
from ..schemas.chat_schema import MessageBase, RoomBase, MediaMessageBase

# common
import aiofiles
from copy import deepcopy
from ...error.errorHandling import HttpException
from ...utils.generateId_util import generate_id
from ...utils.updateTable_util import updateTable
from datetime import datetime
import os

async def startChat(user : dict,message : AddMessageRequest,session : AsyncSession) -> MessageBase :
    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser)).where(Room.roomUser.any(or_(RoomUsers.user_id == user["id"],RoomUsers.user_id == message.receiver_id))))).scalars().all()

    # mencari room yang berisi user dengan user id == id pengirim dan user id == id penerima
    roomExist = None
    for room in findRoom :
        if len(room.roomUser) == 2 :
            isSameRoom=False
            for roomUser in room.roomUser :
                if roomUser.user_id == user["id"] or roomUser.user_id == message.receiver_id :
                    isSameRoom = True
                else :
                    isSameRoom=False
                    break
            if isSameRoom :
                roomExist = room
                break
            
    print(roomExist)
    room_id = None
    # roomForResponse = {}
    if roomExist is None :
        roomMapping = {"id" : generate_id(),"created_at" : datetime.utcnow(),"updated_at" : datetime.utcnow()}
        roomUsersDb = [RoomUsers(**{"id" : generate_id(),"user_id" : user["id"],"room_id" : roomMapping["id"],"deleted" : False}),RoomUsers(**{"id" : generate_id(),"user_id" : message.receiver_id,"room_id" : roomMapping["id"],"deleted" : False})]

        room_id = roomMapping["id"]

        session.add(Room(**roomMapping))
        session.add_all(roomUsersDb)

        # roomForResponse = {**roomMapping}
    else :
        roomUser = list(filter(lambda roomuser: roomuser.user_id == user["id"], roomExist.roomUser))[0]
        if roomUser.deleted :
            roomUser.deleted = False
        
        room_id = findRoom[0].id

        # roomForResponse = deepcopy(findRoom[0].__dict__)
    
    messageMapping = {"id" : generate_id(),"room_id" : room_id,"message" : message.message,"sender_id" : user["id"],"receiver_id" : message.receiver_id,"id_package" : None,"is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow() }
    session.add(Message(**messageMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : messageMapping
    }

async def newMessage(user : dict,room_id : int,message : AddMessageRequest,session : AsyncSession) -> MessageBase :
    findRoom = (await session.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()

    if not findRoom :
        raise HttpException(404,"room is not found")
    
    messageMapping = {"id" : generate_id(),"room_id" : room_id,"message" : message.message,"sender_id" : user["id"],"receiver_id" : message.receiver_id,"id_package" : None,"is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow() }
    session.add(Message(**messageMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : messageMapping
    }

async def updateMessage(user : dict,message_id : int,message : UpdateMessageRequest,session : AsyncSession) -> MessageBase :
    findMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()

    if not findMessage :
        raise HttpException(404,"message is not found")
    
    if findMessage.sender_id != user["id"] :
        raise HttpException(403,"just sender can update message")

    findMessage.message = message.message
    findMessage.updated_at = datetime.utcnow()

    messageDictCopy = deepcopy(findMessage.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : messageDictCopy
    }

async def deleteMessage(user : dict,message_id : int,session : AsyncSession) -> MessageBase :
    findMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()

    if not findMessage :
        raise HttpException(404,"message is not found")
    
    if findMessage.sender_id != user["id"] :
        raise HttpException(403,"just sender can delete message")

    messageDictCopy = deepcopy(findMessage.__dict__)
    await session.delete(findMessage)
    await session.commit()

    return {
        "msg" : "success",
        "data" : messageDictCopy
    }

CHAT_MEDIA_STORE = os.getenv("CHAT_MEDIA_BASE_STORE")
CHAT_MEDIA_BASE_URL = os.getenv("CHAT_MEDIA_BASE_URL")

async def addMediaMessage(message_id : int,file : UploadFile, session : AsyncSession) -> MediaMessageBase :
    ext_file = file.filename.split(".")
    file_name = f"{generate_id()}-{file.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{CHAT_MEDIA_STORE}{file_name}"

    mediaMessageResponse = {}
    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(file.file.read())
        mediaMessageMapping = {"id" : generate_id(),"type" : file.content_type,"url" : f"{CHAT_MEDIA_BASE_URL}/{file_name}","message_id" : message_id}
        session.add(MediaMessage(**mediaMessageMapping))
        await session.commit()
        mediaMessageResponse = mediaMessageMapping
    
    return {
        "msg" : "success",
        "data" : mediaMessageResponse
    }

async def readMessage(user : dict,room_id : int,session : AsyncSession) :
    await session.execute(
        text("UPDATE message SET is_read = true where receiver_id = :user_id and room_id = :room_id"),
        {"user_id": user["id"],"room_id" : room_id}
    )
    await session.commit()

    return {
        "msg" : "success"
    }


async def getAllRoom(user : dict,query : GetRoomQuery,session : AsyncSession) -> GetRoomResponse :
    # ,Room.roomUser.any(RoomUsers.user.and_(User.name.ilike(f"%{query.receiver_name}%"))) if query.receiver_name else True
    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser.and_(RoomUsers.user_id != user["id"])).joinedload(RoomUsers.user),subqueryload(Room.messages).options(subqueryload(Message.media),joinedload(Message.package))).where(and_(Room.roomUser.any(and_(RoomUsers.user_id == user["id"],RoomUsers.deleted == False)))))).scalars().all()

    response = []

    for room in findRoom :
        if len(room.roomUser) != 0 :
            count_not_read = len(list(filter(lambda message: message.is_read == False and message.receiver_id == user["id"], room.messages)))
            
            response.append({"room_id" : room.id,"to_user_name" : room.roomUser[0].user.name,"to_user_id" : room.roomUser[0].user_id,"last_message" : room.messages[-1].message,"last_message_time" : room.messages[-1].created_at,"count_not_read_message" : count_not_read})

    return {
        "msg" : "success",
        "data" : response
    }

async def getMessageInsideRoom(room_id : int,session : AsyncSession) -> list[MessageBase] :
    findMessage = (await session.execute(select(Message).options(joinedload(Message.package),subqueryload(Message.media)).where(Message.room_id == room_id).order_by(Message.created_at.desc()))).scalars().all()

    return {
        "msg" : "success",
        "data" : findMessage
    }

async def deleteRoom(user : dict,room_id : int,session : AsyncSession) :
    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser)).where(Room.id == room_id))).scalar_one_or_none()

    if not findRoom :
        raise HttpException(404,"room is not found")
    
    myRoom = list(filter(lambda roomuser: roomuser.user_id == user["id"], findRoom.roomUser))[0]
    receiverRoom = list(filter(lambda roomuser: roomuser.user_id != user["id"], findRoom.roomUser))[0]

    if receiverRoom.deleted :
        session.delete(findRoom)
    else :
        myRoom.deleted = True
    
    await session.commit()

    return {
        "msg" : "Delete Room Success"
    }
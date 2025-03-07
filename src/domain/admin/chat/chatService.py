from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_,or_
from fastapi import UploadFile
from sqlalchemy.orm import joinedload, subqueryload
# models
from ....models.user_model import User
from ....models.chat_model import RoomUsers,Room,Message,MediaMessage

# schemas
from .chatSchema import AddMessageRequest, UpdateMessageRequest, GetRoomQuery
from ...schemas.chat_schema import MessageBase, RoomBase, MediaMessageBase

# common
import aiofiles
from copy import deepcopy
from ....error.errorHandling import HttpException
from ....utils.generateId_util import generate_id
from ....utils.updateTable_util import updateTable
from datetime import datetime
import os

async def startChat(admin : dict,message : AddMessageRequest,session : AsyncSession) -> MessageBase :
    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser)).where(Room.messages.any(and_(RoomUsers.user_id == admin["id"],RoomUsers.user_id == message.receiver_id))))).scalars().all()

    room_id = None
    # roomForResponse = {}
    if len(findRoom) == 0 :
        roomMapping = {"id" : generate_id(),"created_at" : datetime.utcnow(),"updated_at" : datetime.utcnow()}
        roomUsersDb = [RoomUsers(**{"id" : generate_id(),"user_id" : admin["id"],"room_id" : roomMapping["id"],"deleted" : False})]

        room_id = roomMapping["id"]

        session.add(Room(**roomMapping))
        session.add_all(roomUsersDb)

        # roomForResponse = {**roomMapping}
    else :
        roomUser = list(filter(lambda roomuser: roomuser.user_id == admin["id"], findRoom[0].roomUser))[0]
        if roomUser.deleted :
            roomUser.deleted = False
        
        room_id = findRoom[0].id

        # roomForResponse = deepcopy(findRoom[0].__dict__)
    
    messageMapping = {"id" : generate_id(),"room_id" : room_id,"message" : message.message,"sender_id" : admin["id"],"receiver_id" : message.receiver_id,"id_package" : None,"is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow() }
    session.add(Message(**messageMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : messageMapping
    }

async def newMessage(admin : dict,room_id : int,message : AddMessageRequest,session : AsyncSession) -> MessageBase :
    findRoom = (await session.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()

    if not findRoom :
        raise HttpException(404,"room is not found")
    
    messageMapping = {"id" : generate_id(),"room_id" : room_id,"message" : message.message,"sender_id" : admin["id"],"receiver_id" : message.receiver_id,"id_package" : None,"is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow() }
    session.add(Message(**messageMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : messageMapping
    }

async def updateMessage(admin : dict,message_id : int,message : UpdateMessageRequest,session : AsyncSession) -> MessageBase :
    findMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()

    if not findMessage :
        raise HttpException(404,"message is not found")
    
    if findMessage.sender_id != admin["id"] :
        raise HttpException(403,"just sender can update message")

    findMessage.message = message.message
    findMessage.updated_at = datetime.utcnow()

    messageDictCopy = deepcopy(findMessage.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : messageDictCopy
    }

async def deleteMessage(admin : dict,message_id : int,session : AsyncSession) -> MessageBase :
    findMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()

    if not findMessage :
        raise HttpException(404,"message is not found")
    
    if findMessage.sender_id != admin["id"] :
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

async def getAllRoom(admin : dict,query : GetRoomQuery,session : AsyncSession) -> list[RoomBase] :
    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser.any(RoomUsers.user_id != admin["id"])).joinedload(RoomUsers.user),subqueryload(Room.messages).options(subqueryload(Message.media),joinedload(Message.package))).where(and_(Room.roomUser.any(RoomUsers.user_id == admin["id"]),Room.roomUser.any(RoomUsers.user.and_(User.name.like(f"%{query.receiver_name}%"))) if query.receiver_name else True)))).scalars().all()

    return {
        "msg" : "success",
        "data" : findRoom
    }

async def getMessageInsideRoom(room_id : int,session : AsyncSession) -> MessageBase :
    findMessage = (await session.execute(select(Message).options(joinedload(Message.package),subqueryload(Message.media)).where(Message.room_id == room_id))).scalars().all()

    return {
        "msg" : "success",
        "data" : findMessage
    }

async def deleteRoom(admin : dict,room_id : int,session : AsyncSession) :
    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser)).where(Room.id == room_id))).scalar_one_or_none()

    if not findRoom :
        raise HttpException(404,"room is not found")
    
    myRoom = list(filter(lambda roomuser: roomuser.user_id == admin["id"], findRoom))[0]
    receiverRoom = list(filter(lambda roomuser: roomuser.user_id != admin["id"], findRoom))[0]

    if receiverRoom.deleted :
        session.delete(findRoom)
    else :
        myRoom.deleted = True
    
    await session.commit()

    return {
        "msg" : "success"
    }
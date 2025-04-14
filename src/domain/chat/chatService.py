from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_,or_,text
from fastapi import UploadFile
from sqlalchemy.orm import joinedload, subqueryload, selectinload
# models
from ...models.user_model import User
from ...models.chat_model import RoomUsers,Room,Message,MediaMessage
from ...models.package_model import Package,PackagePrices

# schemas
from .chatSchema import AddMessageRequest, UpdateMessageRequest, GetRoomQuery, GetRoomResponse
from ..schemas.chat_schema import MessageBase, RoomBase, MediaMessageBase

# common
import aiofiles
from copy import deepcopy
from ...error.errorHandling import HttpException
from ...utils.generateId_util import generate_id
from datetime import datetime
import os
from ...socket.socket_connection_handling import sio,getUserSid


async def startChat(user : dict,message : AddMessageRequest,session : AsyncSession) -> MessageBase :
    findUser = (await session.execute(select(User).where(User.id == message.receiver_id))).scalar_one_or_none()

    if not findUser :
        raise HttpException(404,"user not found")
    
    if message.package_id :
        findPackage = (await session.execute(select(Package).where(Package.id == message.package_id))).scalar_one_or_none()

        if findPackage is None :
            raise HttpException(404,"package is not found")
    
    if message.package_prices_id :
        findPackagePrice = (await session.execute(select(PackagePrices).where(PackagePrices.id == message.package_prices_id))).scalar_one_or_none()

        if findPackagePrice is None :
            raise HttpException(404,"package price is not found")

    
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
    
    messageMapping = {"id" : generate_id(),"room_id" : room_id,"message" : message.message,"sender_id" : user["id"],"receiver_id" : message.receiver_id,"id_package" : message.package_id,"package_prices_id" : message.package_prices_id, "is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow() }
    session.add(Message(**messageMapping))
    await session.commit()
    await session.refresh(findUser)

    # send new room to socket client
    user_sid = await getUserSid(findUser.id)
    if user_sid :
        await sio.emit("start_chat",{"room_id" : room_id,"to_user_name" : findUser.name,"to_user_id" : findUser.name,"last_message" : message.message,"last_message_time" : messageMapping["created_at"],"count_not_read_message" : 1},user_sid) 

    return {
        "msg" : "success",
        "data" : messageMapping
    }

async def newMessage(user : dict,room_id : int,message : AddMessageRequest,session : AsyncSession) -> MessageBase :
    findRoom = (await session.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()

    if not findRoom :
        raise HttpException(404,"room is not found")
    
    findUser = (await session.execute(select(User).where(User.id == message.receiver_id))).scalar_one_or_none()

    if not findUser :
        raise HttpException(404,"user not found")
    
    if message.package_prices_id :
        findPackagePrice = (await session.execute(select(PackagePrices).where(PackagePrices.id == message.package_prices_id))).scalar_one_or_none()

        if findPackagePrice is None :
            raise HttpException(404,"package price is not found")
    
    packageDictCopy = None
    if message.package_id :
        findPackage = (await session.execute(select(Package).where(Package.id == message.package_id))).scalar_one_or_none()

        if findPackage is None :
            raise HttpException(404,"package is not found")
        
        packageDictCopy = deepcopy(findPackage.__dict__)
        packageDictCopy.pop("_sa_instance_state")
    
    packagePriceDictCopy = None
    if message.package_prices_id :
        findPackagePrice = (await session.execute(select(PackagePrices).where(PackagePrices.id == message.package_prices_id))).scalar_one_or_none()

        if findPackagePrice is None :
            raise HttpException(404,"package price is not found")

        packagePriceDictCopy = deepcopy(findPackagePrice.__dict__)
        packagePriceDictCopy.pop("_sa_instance_state")
    
    messageMapping = {"id" : generate_id(),"room_id" : room_id,"message" : message.message,"sender_id" : user["id"],"receiver_id" : message.receiver_id,"id_package" : message.package_id,"is_read" : False,"created_at" : datetime.utcnow() ,"updated_at" : datetime.utcnow() }
    session.add(Message(**messageMapping))
    await session.commit()

    # send new message to socket client
    user_sid = await getUserSid(messageMapping["receiver_id"])
    if user_sid :
        await sio.emit("new_message",{**messageMapping,"package" : packageDictCopy,"package_price" : packagePriceDictCopy})

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
    messageDictCopy.pop("_sa_instance_state") # pop that, so that can send for socket connection
    await session.commit()

    # update message to socket client
    user_sid = await getUserSid(messageDictCopy["receiver_id"])
    if user_sid :
        await sio.emit("update_message",messageDictCopy)

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
    messageDictCopy.pop("_sa_instance_state") # pop that, so that can send for socket connection
    await session.delete(findMessage)
    await session.commit()

    # update message to socket client
    user_sid = await getUserSid(messageDictCopy["receiver_id"])
    if user_sid :
        await sio.emit("delete_message",messageDictCopy)

    return {
        "msg" : "success",
        "data" : messageDictCopy
    }

CHAT_MEDIA_STORE = os.getenv("CHAT_MEDIA_BASE_STORE")
CHAT_MEDIA_BASE_URL = os.getenv("CHAT_MEDIA_BASE_URL")

async def addMediaMessage(message_id : int,file : UploadFile, session : AsyncSession) -> MediaMessageBase :
    findMessage = (await session.execute(select(Message).where(Message.id == message_id))).scalar_one_or_none()

    if not findMessage:
        raise HttpException(404,"message is not found")
    
    ext_file = file.filename.split(".")
    file_name = f"{generate_id()}-{file.filename.split(' ')[0]}.{ext_file[-1]}"
    file_name_save = f"{CHAT_MEDIA_STORE}{file_name}"

    mediaMessageResponse = {}
    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(file.file.read())
        mediaMessageMapping = {"id" : generate_id(),"type" : file.content_type,"url" : f"{CHAT_MEDIA_BASE_URL}/{file_name}","message_id" : message_id}
        session.add(MediaMessage(**mediaMessageMapping))
        await session.commit()
        await session.refresh(findMessage)
        mediaMessageResponse = mediaMessageMapping
    
    # send media message to socket client
    user_sid = await getUserSid(findMessage.receiver_id)
    if user_sid :
        await sio.emit("new_media_message",mediaMessageResponse)

    return {
        "msg" : "success",
        "data" : mediaMessageResponse
    }

async def readMessage(user : dict,room_id : int,session : AsyncSession) :
    findRoom = (await session.execute(select(Room).options(subqueryload(Room.roomUser.and_(RoomUsers.user_id != user["id"]))).where(Room.id == room_id))).scalar_one_or_none()

    if findRoom is None :
        raise HttpException(404,"room is not found")
    await session.execute(
        text("UPDATE message SET is_read = true where receiver_id = :user_id and room_id = :room_id"),
        {"user_id": user["id"],"room_id" : room_id}
    )
    await session.commit()
    await session.refresh(findRoom)

    # send media message to socket client
    user_sid = await getUserSid(findRoom.roomUser[0].user_id) if len(findRoom.roomUser) > 0 else None
    if user_sid :
        await sio.emit("read_message",{"room_id" : room_id})

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
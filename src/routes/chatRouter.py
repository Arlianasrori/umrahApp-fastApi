from fastapi import APIRouter, Depends, UploadFile
# service
from ..domain.chat import chatService

# db
from ..db.sessionDepedency import sessionDepedency
# schemas
from ..domain.chat.chatSchema import AddMessageRequest, UpdateMessageRequest, GetRoomQuery, GetRoomResponse
from ..domain.schemas.chat_schema import MessageBase,MediaMessageBase
from ..domain.schemas.response_schema import ApiResponse,MessageOnlyResponse
# depends
from ..auth.auth_depends.alluser.depend_auth_alluser import allUserAuth
from ..auth.auth_depends.alluser.get_alluser_auth import getAllUserAuth

chatRouter = APIRouter(prefix="/chat",dependencies=[Depends(allUserAuth)])

@chatRouter.post("/start_chat",response_model=ApiResponse[MessageBase],description="used to start a chat with other users or create a room.",tags=["CHAT/ROOM"])
async def start_chat(message : AddMessageRequest,user : dict = Depends(getAllUserAuth),session : sessionDepedency = None) :
    return await chatService.startChat(user,message,session)

@chatRouter.get("/room",response_model=ApiResponse[list[GetRoomResponse]],description="used to start a chat with other users or create a room.",tags=["CHAT/ROOM"])
async def getAllRoom(query : GetRoomQuery = Depends(),user : dict = Depends(getAllUserAuth),session : sessionDepedency = None) :
    return await chatService.getAllRoom(user,query,session)

@chatRouter.delete("/room/{room_id}",response_model=MessageOnlyResponse,description="used to start a chat with other users or create a room.",tags=["CHAT/ROOM"])
async def deleteRoom(room_id : int,user : dict = Depends(getAllUserAuth),session : sessionDepedency = None) :
    return await chatService.deleteRoom(user,room_id,session)


@chatRouter.get("/message/{room_id}",response_model=ApiResponse[list[MessageBase]],description="used to start a chat with other users or create a room.",tags=["CHAT/MESSAGE"])
async def getAllMessageInsideRoom(room_id : int,session : sessionDepedency = None) :
    return await chatService.getMessageInsideRoom(room_id,session)

@chatRouter.post("/message/{room_id}",response_model=ApiResponse[MessageBase],description="used to start a chat with other users or create a room.",tags=["CHAT/MESSAGE"])
async def new_message(room_id : int,message : AddMessageRequest,user : dict = Depends(getAllUserAuth),session : sessionDepedency = None) :
    return await chatService.newMessage(user,room_id,message,session)

@chatRouter.put("/message/{message_id}",response_model=ApiResponse[MessageBase],description="used to start a chat with other users or create a room.",tags=["CHAT/MESSAGE"])
async def update_message(message_id : int,message : UpdateMessageRequest,user : dict = Depends(getAllUserAuth),session : sessionDepedency = None) :
    return await chatService.updateMessage(user,message_id,message,session)

@chatRouter.delete("/message/{message_id}",response_model=ApiResponse[MessageBase],description="used to start a chat with other users or create a room.",tags=["CHAT/MESSAGE"])
async def delete_message(message_id : int,user : dict = Depends(getAllUserAuth),session : sessionDepedency = None) :
    return await chatService.deleteMessage(user,message_id,session)

@chatRouter.post("/message/media/{message_id}",response_model=ApiResponse[MediaMessageBase],description="used to start a chat with other users or create a room.",tags=["CHAT/MESSAGE"])
async def add_media_message(message_id : int,file : UploadFile,session : sessionDepedency = None) :
    return await chatService.addMediaMessage(message_id,file,session)

@chatRouter.get("/message/read/{room_id}",response_model=MessageOnlyResponse,tags=["CHAT/MESSAGE"])
async def read_message(room_id : int,user : dict = Depends(getAllUserAuth),session : sessionDepedency = None) :
    return await chatService.readMessage(user,room_id,session)
from sqlalchemy import Column, DateTime,String,Boolean,Enum,ForeignKey,Integer
from sqlalchemy.orm import relationship
from ..db.db import Base
import datetime

class RoomUsers(Base):
    __tablename__ = "room_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id',ondelete="CASCADE"))
    room_id = Column(Integer, ForeignKey('room.id',ondelete="CASCADE"))
    deleted = Column(Boolean, default=False) 

    room = relationship("Room",back_populates="roomUser")
    user = relationship("User",back_populates="roomUser")

    def __repr__(self):
        return f"<RoomUser(roomId={self.room_id}, userID={self.user_id})>"

class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
    messages = relationship("Message", back_populates="room")
    roomUser = relationship("RoomUsers",back_populates="room")

    def __repr__(self):
        return f"<Room(id={self.id})>"

class Message(Base) :
    __tablename__ = "message"

    id = Column(Integer,primary_key=True)
    room_id = Column(Integer,ForeignKey("room.id"),nullable=False)
    message = Column(String,nullable=False)
    sender_id = Column(Integer,ForeignKey("user.id"),nullable=False)
    receiver_id = Column(Integer,ForeignKey("user.id"),nullable=False)
    id_package = Column(Integer,ForeignKey("package.id"),nullable=True)
    is_read = Column(Boolean,nullable=False,default=False)
    created_at = Column(DateTime,nullable=False,default=datetime.datetime.utcnow())
    updated_at = Column(DateTime,nullable=False,default=datetime.datetime.utcnow(),onupdate=datetime.datetime.utcnow())

    sender = relationship("User",foreign_keys=[sender_id],back_populates="message_sender")
    receiver = relationship("User",foreign_keys=[receiver_id],back_populates="message_receiver")
    room = relationship("Room",back_populates="messages")
    package = relationship("Package",back_populates="messages")
    media = relationship("MediaMessage",back_populates="message")

    def __repr__(self) -> str:
        return f"Chat(id={self.id}, message={self.message}, sender_id={self.sender_id}, receiver_id={self.receiver_id})"
    
class MediaMessage(Base):
    __tablename__ = "media_message"

    id = Column(Integer, primary_key=True)
    type = Column(String)  # Type of media (image, video, etc.)
    url = Column(String)
    message_id = Column(Integer, ForeignKey("message.id"))

    message = relationship("Message",back_populates="media")

    def __repr__(self) -> str:
        return f"media {self.message_id}-{self.type}-{self.url}"
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float,Boolean
from sqlalchemy.orm import relationship
from ..db.db import Base
from ..types.user_types import UserRoleEnum

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String,nullable=True)
    role = Column(Enum(UserRoleEnum), nullable=False)
    foto_profile = Column(String,nullable=True)
    verified = Column(Boolean,default=False)                                                                            

    booking = relationship("Booking", back_populates="user")
    rating = relationship("Rating", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    notification_reads = relationship("NotificationRead", back_populates="user")
    roomUser = relationship("RoomUsers",back_populates="users")
    message_sender = relationship("Message",foreign_keys="[Message.sender_id]",back_populates="sender")
    message_receiver = relationship("Message",foreign_keys="[Message.receiver_id]",back_populates="receiver")
    otp = relationship("OtpCode",back_populates="user")

    def __repr__(self):
        return f"<User(name={self.name}, role={self.role})>"

class OtpCode(Base) :
    __tablename__ = 'otp'
    
    id = Column(Integer, primary_key=True)  
    user_id = Column(Integer,ForeignKey('user.id'), nullable=False)
    otp = Column(Integer, nullable=False) 
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User",back_populates="otp")

    def __repr__(self):
        return f"<Otp(user_id={self.user_id}, otp={self.otp})>"
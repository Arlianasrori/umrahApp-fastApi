from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,DateTime, Enum
from sqlalchemy.orm import relationship
from ..db.db import Base
from datetime import datetime
from ..types.notification_types import NotificationDataEnum

class Notification(Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(255))
    body = Column(String(1500))
    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="notifications")
    reads = relationship("NotificationRead", back_populates="notification")
    data = relationship("NotificationData",backref="notification",uselist=False)

    def __repr__(self):
        return f"<Notification(id={self.id}, title={self.title})>"

class NotificationRead(Base):
    __tablename__ = 'notification_read'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    notification_id = Column(Integer, ForeignKey('notification.id'))
    is_read = Column(Boolean, default=True)

    notification = relationship("Notification", back_populates="reads")
    user = relationship("User", back_populates="notification_reads")

    def __repr__(self):
        return f"<NotificationRead(id={self.id})>"

class NotificationData(Base) :
    __tablename__ = "notification_data"
    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notification.id'), nullable=False)
    data_id = Column(Integer,nullable=False)
    data_type = Column(Enum(NotificationDataEnum),nullable=False)
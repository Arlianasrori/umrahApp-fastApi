from sqlalchemy import Column, Integer, String, ForeignKey, Date,Enum, Float, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from ..db.db import Base
from ..types.package_types import PackageTypeEnum,RoomTypeEnum, BookingStatusEnum, PackageCategoryEnum
import datetime


class Package(Base):
    __tablename__ = 'package'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    departure_date = Column(Date, nullable=False)
    image = Column(String, nullable=False)
    detail = Column(String)
    category = Column(Enum(PackageCategoryEnum))
    add_by_admin = Column(Integer,ForeignKey("user.id"), nullable=False)

    package_prices = relationship("PackagePrices", back_populates="package")
    user = relationship("User", back_populates="package")
    booking = relationship("Booking", back_populates="package")
    rating = relationship("Rating", back_populates="package")
    gallery = relationship("GalleryPackage", back_populates="package")

    def __repr__(self):
        return f"<Package(id={self.id}, name={self.name})>"

class GalleryPackage(Base) :
    __tablename__ = 'gallery_package'

    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("package.id"), nullable=False)
    image = Column(String, nullable=False)

    package = relationship("Package", back_populates="gallery")

class PackagePrices(Base) :
    __tablename__ = 'package_prices'

    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("package.id"), nullable=False)
    package_type = Column(Enum(PackageTypeEnum), nullable=False)
    room_type = Column(Enum(RoomTypeEnum), nullable=False)
    price = Column(Float, nullable=False)
    detail = Column(String)
    seat_count = Column(Integer, nullable=False)


    package = relationship("Package", back_populates="package_prices")
    booking = relationship("Booking", back_populates="package_price")

    def __repr__(self):
        return f"<PackagePrices(id={self.id}, type={self.package_type} roomType={self.room_type})>"

class Booking(Base):
    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    package_id = Column(Integer,ForeignKey("package.id"), nullable=False)
    packages_price_id = Column(Integer, ForeignKey("package_prices.id"),nullable=False)
    booking_date = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatusEnum))
    count = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    package = relationship("Package", back_populates="booking")
    user = relationship("User", back_populates="booking")
    package_price = relationship("PackagePrices", back_populates="booking")

    def __repr__(self):
        return f"<Booking(id={self.id})>"

class Rating(Base):
    __tablename__ = 'rating'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey("user.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("package.id"),nullable=False)
    rating = Column(Float, nullable=False)
    review = Column(String)
    created_at = Column(DateTime,default=datetime.datetime.now())

    user = relationship("User", back_populates="rating")
    package = relationship("Package", back_populates="rating")

    __table_args__ = (
        CheckConstraint('rating <= 5', name='rating_lessorequal_five'),
    )

    def __repr__(self):
        return f"<Otp(id={self.id} user_id={self.user_id}, package_id={self.package_id})>"
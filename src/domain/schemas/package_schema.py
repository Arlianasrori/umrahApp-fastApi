from pydantic import BaseModel
from ...types.package_types import PackageTypeEnum,RoomTypeEnum,BookingStatusEnum
from .user_schema import UserBase
from datetime import datetime, date

class PackageBase(BaseModel) :
    id : int
    name : str
    departure_date : date
    image : str
    detail : str

class GalleryPackageBase(BaseModel) :
    id : int
    image : str

class PackagePricesBase(BaseModel) :
    id : int
    package_type : PackageTypeEnum
    room_type : RoomTypeEnum
    price : float
    detail : str
    seat_count : int

class BookingBase(BaseModel) :
    id : int
    user_id : int
    package_id : int
    packages_price_id : int
    booking_date : int
    status : BookingStatusEnum
    total_price : float

class RatingBase(BaseModel) :
    id : int
    package_id : int
    rating : int
    review : str
    created_at : datetime

class RatingWithUser(RatingBase) :
    user : UserBase

class RatingWithUserPackage(RatingBase) :
    user : UserBase
    package : PackageBase

class BookingWithUserPrice(BookingBase) :
    user : UserBase
    package_price : PackagePricesBase

class PackageWithPrices(PackageBase) :
    package_prices : list[PackagePricesBase]

class PackageWithGallery(PackageBase) :
    gallery : list[GalleryPackageBase]

class PackageWithPricesAndGallery(PackageBase) :
    package_prices : list[PackagePricesBase]
    gallery : list[GalleryPackageBase]

class PackageWithPricesGalleryUser(PackageBase) :
    package_prices : list[PackagePricesBase]
    gallery : list[GalleryPackageBase]
    user : list[UserBase]

class PackageWithBooking(PackageBase) :
    booking : list[BookingWithUserPrice]
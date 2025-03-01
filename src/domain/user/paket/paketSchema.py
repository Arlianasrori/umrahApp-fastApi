from pydantic import BaseModel, Field
from fastapi import Form,UploadFile,File
from ...schemas.user_schema import UserBase
from ...schemas.package_schema import RatingWithUser, PackageWithPrices,PackagePricesBase
from ....types.package_types import RoomTypeEnum,PackageTypeEnum, PackageCategoryEnum
from datetime import date

class GetAllPackagesQuery(BaseModel) :
    name : str | None = None
    category : PackageCategoryEnum | None = None
    departure_date : date | None = None
    package_type : PackageTypeEnum | None = None
    room_type : RoomTypeEnum | None = None
    min_harga : int | None = None
    max_harga : int | None = None
    limit : int | None= None

class GetAllPackagesResponse(BaseModel) :
    package : PackageWithPrices
    avg_rating : float | None

class GetStatistikRating(BaseModel) :
    count_rating : int = 0
    count_reviews : int = 0
    avg_rating : float | None
    count_5 : int = 0
    count_4 : int = 0
    count_3 : int = 0
    count_2 : int = 0
    count_1 : int = 0

class GetPackagePriceResponse(BaseModel) :
    package_price : PackagePricesBase
    count_seat_avaliable : int

class AddRatingRequest(BaseModel) :
    package_id : int
    rating : int = Field(ge=1,le=5)
    review : str | None = None

class UpdateRatingRequest(BaseModel) :
    rating : int | None = Field(ge=1,le=5,default=None)
    review : str | None = None

class GetPackageRatingResponse(BaseModel) :
    statistik : GetStatistikRating
    reviews :  list[RatingWithUser]

class GetRombonganPackageResponse(BaseModel) :
    count_filled : int = 0
    count_booking : int = 0
    count_available : int = 0
    user : list[UserBase]
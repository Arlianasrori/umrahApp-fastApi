from pydantic import BaseModel
from fastapi import Form,UploadFile,File
from ...schemas.package_schema import PackageBase, RatingWithUser
from ...schemas.pagination_schema import PaginationBase
from ....types.package_types import RoomTypeEnum,BookingStatusEnum,PackageTypeEnum
from datetime import date
class ResponsePaketPag(PaginationBase) :
    data : list[PackageBase] = []

class AddPackageRequest(BaseModel) :
    name : str
    seat_count : int
    departure_date : date
    image : UploadFile
    detail : str
    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            seat_count: int = Form(...),
            departure_date: date = Form(...),
            image: UploadFile = File(...),
            detail: str = Form(...)
        ):
            return cls(
                name=name,
                seat_count=seat_count,
                departure_date=departure_date,
                image=image,
                detail=detail
            )
    
class UpdatePackageRequest(BaseModel) :
    name : str | None = None
    seat_count : int | None = None
    departure_date : date | None = None
    image : UploadFile | None = None
    detail : str | None = None
    @classmethod
    def as_form(
            cls,
            name: str | None = Form(None),
            seat_count: int | None = Form(None),
            departure_date: date | None = Form(None),
            image: UploadFile | None = File(None),
            detail: str | None = Form(None)
        ):
            return cls(
                name=name,
                seat_count=seat_count,
                departure_date=departure_date,
                image=image,
                detail=detail
            )

class PackagePrices(BaseModel) :
    package_type : PackageTypeEnum
    room_type : RoomTypeEnum
    price : float

class AddPackagePricesRequest(BaseModel) :
    package_id : int
    package_prices : list[PackagePrices]

class UpdatePackagePricesRequest(BaseModel) :
    package_type : PackageTypeEnum | None = None
    room_type : RoomTypeEnum | None = None
    price : float | None = None

class GetAllPackagesQuery(BaseModel) :
    page : int | None = None
    limit : int = 10
    start_date : date | None = None
    end_date : date | None = None

class GetStatistikRating(BaseModel) :
    count_rating : int = 0
    count_reviews : int = 0
    avg_rating : float | None
    count_5 : int = 0
    count_4 : int = 0
    count_3 : int = 0
    count_2 : int = 0
    count_1 : int = 0

class GetPackageRatingResponse(BaseModel) :
    statistik : GetStatistikRating
    reviews :  list[RatingWithUser]
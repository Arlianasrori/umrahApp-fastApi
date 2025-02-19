from pydantic import BaseModel
from fastapi import Form,UploadFile,File
from ...schemas.package_schema import PackageBase
from ...schemas.pagination_schema import PaginationBase
from ....types.package_types import RoomTypeEnum,BookingStatusEnum,PackageTypeEnum
from datetime import date


class GetPackageContainsBooking(PaginationBase) :
    package : PackageBase
    count_booking : int
    count_booking_pending : int
    count_booking_confirmed : int
    count_booking_canceled : int

class GetPackageContainsBookingResponsePag(PaginationBase) :
    data : list[GetPackageContainsBooking]

class GetAllPackagesQuery(BaseModel) :
    page : int | None = None
    limit : int = 10
    start_date : date | None = None
    end_date : date | None = None

class UpdateBookingStatusRequest(BaseModel) :
    status : BookingStatusEnum
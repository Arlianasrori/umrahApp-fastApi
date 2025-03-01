from pydantic import BaseModel
from fastapi import Form,UploadFile,File
from ...schemas.user_schema import UserBase
from ...schemas.package_schema import PackageBase, RatingWithUser, PackageWithPrices
from ...schemas.pagination_schema import PaginationBase
from ....types.package_types import RoomTypeEnum,BookingStatusEnum,PackageTypeEnum, PackageCategoryEnum
from datetime import date

class AddBookingRequest(BaseModel) :
    package_id : int
    packages_price_id : int
    total_price : float
    count : int
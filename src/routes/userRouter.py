from fastapi import APIRouter, Depends, UploadFile
from datetime import date
# auth_profile
from ..domain.user.auth_profile import authProfileService 
from ..domain.user.auth_profile.authProfileModel import UpdateProfileRequest

# package
from ..domain.user.paket import paketService
from ..domain.user.paket.paketSchema import GetAllPackagesQuery, GetPackageRatingResponse, GetAllPackagesResponse, GetRombonganPackageResponse, GetPackagePriceResponse, AddRatingRequest, UpdateRatingRequest
from ..domain.schemas.package_schema import PackageWithGallery,BookingBase, BookingWithPackagePrices, RatingBase, RatingWithUserPackage

# booking
from ..domain.user.booking import bookingService
from ..domain.user.booking.bookiingSchema import AddBookingRequest

# notification
from ..domain.notification_method import notificationService
from ..domain.schemas.notification_schema import NotificationBase,ResponseGetUnreadNotification


# db
from ..db.sessionDepedency import sessionDepedency
# schemas
from ..domain.schemas.response_schema import ApiResponse
from ..domain.schemas.user_schema import UserBase
from ..types.package_types import PackageTypeEnum,RoomTypeEnum
# depends
from ..auth.auth_depends.user.depend_auth_user import userAuth
from ..auth.auth_depends.user.get_user_auth import getUserAuth

userRouter = APIRouter(prefix="/user",dependencies=[Depends(userAuth)])

# auth_profile
@userRouter.get("/",response_model=ApiResponse[UserBase],tags=["USER/AUTH-PROFILE"])
async def get_user(user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await authProfileService.getUser(user["id"],session)

@userRouter.put("/profile",response_model=ApiResponse[UserBase],tags=["USER/AUTH-PROFILE"])
async def get_user(profile : UpdateProfileRequest,user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await authProfileService.updateProfile(user["id"],profile,session)
# package
@userRouter.get("/package",response_model=ApiResponse[list[GetAllPackagesResponse]],tags=["USER/PACKAGE"])
async def get_all_package(query : GetAllPackagesQuery = Depends(),session : sessionDepedency = None) :
    return await paketService.getAllPackage(query,session)

@userRouter.get("/package/{id_package}",response_model=ApiResponse[PackageWithGallery],tags=["USER/PACKAGE"])
async def get_package_by_id(id_package : int,session : sessionDepedency = None) :
    return await paketService.getPackageById(id_package,session)

@userRouter.get("/package/price/{id_package}",response_model=ApiResponse[GetPackagePriceResponse],tags=["USER/PACKAGE"])
async def get_package_price(id_package : int,package_type : PackageTypeEnum,room_type : RoomTypeEnum,session : sessionDepedency = None) :
    return await paketService.getPackagePrice(id_package,package_type,room_type,session)

@userRouter.get("/package/rombongan/{id_package_price}",response_model=ApiResponse[GetRombonganPackageResponse],tags=["USER/PACKAGE"])
async def get_rombongan_package(id_package_price : int,session : sessionDepedency = None) :
    return await paketService.getRombonganPackage(id_package_price,session)

# rating
@userRouter.get("/package/rating/{id_package}",response_model=ApiResponse[GetPackageRatingResponse],tags=["USER/PACKAGE/RATING"])
async def get_package_rating(id_package : int,session : sessionDepedency = None) :
    return await paketService.getPackageRating(id_package,session)

@userRouter.post("/package/rating",response_model=ApiResponse[RatingWithUserPackage],tags=["USER/PACKAGE/RATING"])
async def add_package_rating(rating : AddRatingRequest,user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await paketService.addRating(user,rating,session)

@userRouter.put("/package/rating/{id_rating}",response_model=ApiResponse[RatingBase],tags=["USER/PACKAGE/RATING"])
async def add_package_rating(id_rating : int, rating : UpdateRatingRequest,user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await paketService.updateRating(user,id_rating,rating,session)

@userRouter.delete("/package/rating/{id_rating}",response_model=ApiResponse[RatingBase],tags=["USER/PACKAGE/RATING"])
async def add_package_rating(id_rating : int, user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await paketService.deleteRating(user,id_rating,session)

# booking
@userRouter.post("/booking",response_model=ApiResponse[BookingBase],tags=["USER/BOOKING"])
async def add_booking(request : AddBookingRequest,user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await bookingService.addBooking(user,request,session)

@userRouter.get("/booking",response_model=ApiResponse[list[BookingWithPackagePrices]],tags=["USER/BOOKING"])
async def get_package_booking(user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await bookingService.getPackageBooking(user,session)

@userRouter.put("/booking/{booking_id}",response_model=ApiResponse[BookingBase],tags=["USER/BOOKING"])
async def cancel_booking(booking_id : int,user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await bookingService.cancelBooking(user,booking_id,session)

# notification
@userRouter.get("/notification",response_model=ApiResponse[dict[date,list[NotificationBase]]],tags=["USER/NOTIFICATION"])
async def getAllNotification(user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await notificationService.getAllNotification(user["id"],session)

@userRouter.get("/notification/{id_notification}",response_model=ApiResponse[NotificationBase],tags=["USER/NOTIFICATION"])
async def getNotificationById(id_notification : int,user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await notificationService.getNotificationById(id_notification,user["id"],session)

@userRouter.post("/notification/read/{id_notification}",response_model=ApiResponse[NotificationBase],tags=["USER/NOTIFICATION"])
async def readNotification(id_notification : int,user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await notificationService.readNotification(id_notification,user["id"],session)

@userRouter.get("/notification/unread/count",response_model=ApiResponse[ResponseGetUnreadNotification],tags=["USER/NOTIFICATION"])
async def getUnreadNotification(user : dict = Depends(getUserAuth),session : sessionDepedency = None) :
    return await notificationService.getCountNotification(user["id"],session)
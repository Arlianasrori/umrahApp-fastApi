from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload
# models
from ....models.package_model import Package,Booking

# schemas
from .bookingSchema import GetPackageContainsBookingResponsePag,GetPackageContainsBooking,GetAllPackagesQuery,UpdateBookingStatusRequest
from ...schemas.package_schema import PackageWithBooking, BookingWithUserPrice

# service
from ...notification_method.notificationService import sendNotificationThreadProccess

# types
from ....types.package_types import BookingStatusEnum
from ....types.notification_types import NotificationDataEnum

# common
import math
from ....error.errorHandling import HttpException
from copy import deepcopy

async def getAllPackageContainsBooking(admin : dict,query : GetAllPackagesQuery,session:AsyncSession) -> list[GetPackageContainsBooking] | GetPackageContainsBookingResponsePag:
    statementSelectPackage = select(Package).where(and_(Package.id == admin["id"], Package.departure_date >= query.start_date if query.start_date else True,Package.departure_date <= query.end_date if query.end_date else True))

    statementGetStatistikBooking = select(func.count(Booking.id).label("count_booking"),func.count(Booking.id).filter(Booking.status == BookingStatusEnum.PENDING).label("count_booking_pending"),func.count(Booking.id).filter(Booking.status == BookingStatusEnum.CONFIRMED).label("count_booking_confirmed"),func.count(Booking.id).filter(Booking.status == BookingStatusEnum.CANCELED).label("count_booking_canceled"))

    if query.page :
        findPackage = (await session.execute(statementSelectPackage.limit(10).offset(10 * (query.page - 1)))).scalars().all()
        response = []
        for package in findPackage :
            getStatistikBooking = (await session.execute(statementGetStatistikBooking.where(Booking.package_id == package.id))).one()
            response.append({
                **package.__dict__,
                **getStatistikBooking
            })
            print(getStatistikBooking)
        conntData = (await session.execute(func.count(Package.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "package" : response,
                "count_data" : len(findPackage),
                "count_page" : countPage
            }
        }
    else :
        findPackage = (await session.execute(statementSelectPackage)).scalars().all()
        response = []
        for package in findPackage :
            getStatistikBooking = (await session.execute(statementGetStatistikBooking.where(Booking.package_id == package.id))).one()
            response.append({
                **package.__dict__,
                **getStatistikBooking
            })
        return {
            "msg" : "success",
            "data" : response
        }

async def getDetailBooking(id_package : int,session:AsyncSession) -> PackageWithBooking :
    findPackage = (await session.execute(select(Package).options(joinedload(Package.booking).options(joinedload(Booking.user),joinedload(Booking.package_price))).where(Package.id == id_package))).scalar_one_or_none()

    if not findPackage :
        raise HttpException(404,f"package not found")

    return {
        "msg" : "success",
        "data" : findPackage
    }

async def updateBookingStatus(admin : dict, id_booking : int,request : UpdateBookingStatusRequest,session:AsyncSession) -> BookingWithUserPrice :
    findBooking = (await session.execute(select(Booking).where(and_(Booking.id == id_booking, Booking.package.and_(Package.add_by_admin == admin["id"]))))).scalar_one_or_none()
    if not findBooking :
        raise HttpException(404,f"booking not found")
    
    findBooking.status = request.status

    bookingDictCopy = deepcopy(findBooking.__dict__)
    await session.commit()

    sendNotificationThreadProccess({"user_id" : bookingDictCopy["user_id"],"title" : "Admin Telah Mengupdate Booking Status Anda","body" : f"Admin Telah Mengupdate Booking Status Anda Dengan {bookingDictCopy["status"]}","data_id" : bookingDictCopy["package_id"],"data_type" : NotificationDataEnum.package})

    return {
        "msg" : "success",
        "data" : findBooking
    }
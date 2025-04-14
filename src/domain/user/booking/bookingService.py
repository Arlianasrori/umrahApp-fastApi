from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy import case
# models
from ....models.package_model import Package,PackagePrices, Booking, Rating

# schemas
from .bookiingSchema import AddBookingRequest
from ...schemas.package_schema import BookingBase, PackageWithPrices, BookingWithPackagePrices

# type
from ....models.package_model import BookingStatusEnum

# service
from ...notification_method.notificationService import sendNotificationThreadProccess

# common
from ....error.errorHandling import HttpException
from ....utils.generateId_util import generate_id
from datetime import datetime
from copy import deepcopy

async def addBooking(user : dict, request : AddBookingRequest,session:AsyncSession) -> BookingBase:
    findPackagePrice = (await session.execute(select(PackagePrices).options(joinedload(PackagePrices.package)).where(PackagePrices.id == request.packages_price_id))).scalar_one_or_none()

    if not findPackagePrice:
        raise HttpException(status_code=404,detail="Package price not found")
    
    findBooking = (await session.execute(select(Booking).where(and_(Booking.user_id == user["id"],Booking.packages_price_id == request.packages_price_id,Booking.status != BookingStatusEnum.CANCELLED)))).scalars().all()

    if len(findBooking) > 0 :
        raise HttpException(400,"anda telah membooking package ini")

    booking_stats = (await session.execute(
        select(
            func.count(case(
                (Booking.status == BookingStatusEnum.CONFIRMED, 1),
                else_=None
            )).label("count_filled"),
            func.count(case(
                (Booking.status == BookingStatusEnum.PENDING, 1),
                else_=None
            )).label("count_booking")
        )
        .where(Booking.packages_price_id == request.packages_price_id)
    )).one()._asdict()
    print(booking_stats)
    
    if findPackagePrice.seat_count - (booking_stats["count_filled"] + booking_stats["count_booking"]) < request.count:
        raise HttpException(status_code=400,detail="Seat not available")
    
    bookingMapping = request.model_dump()   
    bookingMapping.update({"id" : generate_id(),"user_id" : user["id"],"booking_date" : datetime.now(),"total_price" : request.total_price,"status" : BookingStatusEnum.PENDING})

    packageDictCopy = deepcopy(findPackagePrice.package.__dict__) 
    session.add(Booking(**bookingMapping))
    await session.commit()
    
    sendNotificationThreadProccess({"user_id" : user["id"],"title" : "Booking Berhasil!","body" : f"Booking berhasil, silahkan melakukan pembayaran"})

    sendNotificationThreadProccess({"user_id" : packageDictCopy["add_by_admin"],"title" : f"{user["name"]} membooking package {packageDictCopy["name"]}","body" : f"{user["name"]} membooking package {packageDictCopy["name"]}, silahkan melanjutkan chat dengan {user['name']} untuk melakukan pembayaran"})

    return {
        "msg" : "success",
        "data" : bookingMapping
    }

async def cancelBooking(user : dict,booking_id : str,session:AsyncSession) -> BookingBase:
    findBooking = (await session.execute(select(Booking).options(joinedload(Booking.package)).where(and_(Booking.id == booking_id,Booking.user_id == user["id"])))).scalar_one_or_none()

    if not findBooking:
        raise HttpException(status_code=404,detail="Booking not found")
    
    findBooking.status = BookingStatusEnum.CANCELLED.value
    bookingDictCopy = deepcopy(findBooking.__dict__)
    await session.commit()

    sendNotificationThreadProccess({"user_id" : user["id"],"title" : "Booking Berhasil Dibatalkan","body" : f"Booking berhasil Dibatalkan"})

    sendNotificationThreadProccess({"user_id" : bookingDictCopy["package"].add_by_admin,"title" : f"{user["name"]} membatalkan booking untuk package {bookingDictCopy['package'].name}","body" : f"{user["name"]} membatalkan booking untuk package {bookingDictCopy['package'].name}"})


    return {
        "msg" : "success",
        "data" : bookingDictCopy       
    }

async def getPackageBooking(user : dict,session:AsyncSession) -> list[BookingWithPackagePrices]:
    findBooking = (await session.execute(select(Booking).options(joinedload(Booking.package),joinedload(Booking.package_price)).where(Booking.user_id == user["id"]))).scalars().all()

    return {
        "msg" : "success",
        "data" : findBooking
    }
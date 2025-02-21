from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from sqlalchemy.orm import joinedload, subqueryload
# models
from ....models.package_model import Package,PackagePrices, Booking, Rating
from ....models.user_model import User

# schemas
from .paketSchema import GetAllPackagesQuery, GetPackageRatingResponse, GetAllPackagesResponse, GetRombonganPackageResponse, GetPackagePriceResponse, AddRatingRequest, UpdateRatingRequest
from ...schemas.package_schema import PackageWithGallery, RatingWithUserPackage, RatingBase

# type
from ....models.package_model import BookingStatusEnum,PackageTypeEnum,RoomTypeEnum

# common
from ....error.errorHandling import HttpException
from ....utils.generateId_util import generate_id
from datetime import datetime
from copy import deepcopy
from ....utils.updateTable_util import updateTable


async def getAllPackage(query : GetAllPackagesQuery,session:AsyncSession) -> list[GetAllPackagesResponse]:
    findAllPackage = (await session.execute(select(Package,func.avg(Rating.rating).label("avg_rating")).options(subqueryload(Package.package_prices),subqueryload(Package.rating)).outerjoin(Rating, Package.id == Rating.package_id).where(and_(Package.name.like(f"%{query.name}%") if query.name else True,Package.category == query.category if query.category else True,Package.departure_date == query.departure_date if query.departure_date else True,Package.package_prices.any(PackagePrices.package_type == query.package_type) if query.package_type else True,Package.package_prices.any(PackagePrices.room_type == query.room_type) if query.room_type else True,Package.package_prices.any(PackagePrices.price == query.min_harga) if query.min_harga else True,Package.package_prices.any(PackagePrices.price == query.max_harga) if query.max_harga else True)).group_by(Package.id))).all()

    print(findAllPackage)

    return {
        "msg" : "success",
        "data" : [{"package" : package[0],"avg_rating" : package[1]} for package in findAllPackage]
    }

async def getPackageById(id_package : int,session:AsyncSession) -> PackageWithGallery:
    findPackage = (await session.execute(select(Package).options(subqueryload(Package.gallery)).where(Package.id == id_package))).scalar_one_or_none()

    if not findPackage :
        raise HttpException(404,f"package not found")

    return {
        "msg" : "success",
        "data" : findPackage
    }

async def getPackagePrice(id_package : int,package_type : PackageTypeEnum,room_type : RoomTypeEnum,session : AsyncSession) -> GetPackagePriceResponse :
    findPackagePrice = (await session.execute(select(PackagePrices).where(and_(PackagePrices.package_id == id_package,PackagePrices.package_type == package_type,PackagePrices.room_type == room_type)))).scalars().all()

    if len(findPackagePrice) == 0 :
        raise HttpException(404,"package price not found")
    
    findStat = (await session.execute(select(func.sum(Booking.count).filter(and_(Booking.packages_price_id == findPackagePrice[0].id,Booking.status != BookingStatusEnum.CANCELLED))))).scalar_one()

    return {
        "msg" : "success",
        "data" : {
            "package_price" : findPackagePrice[0],
            "count_seat_avaliable" : findPackagePrice[0].seat_count - (findStat if findStat else 0)
        }
    }

async def getRombonganPackage(id_package_price : int,session:AsyncSession) -> GetRombonganPackageResponse:
    findPackagePrice = (await session.execute(select(PackagePrices).where(PackagePrices.id == id_package_price))).scalar_one_or_none()

    if not findPackagePrice :
        raise HttpException(404,f"package price not found")

    getStatistikBooking = (await session.execute(select(func.count(Booking.id).filter(Booking.status == BookingStatusEnum.CONFIRMED).label("count_filled"),func.count(Booking.id).filter(Booking.status == BookingStatusEnum.PENDING).label("count_booking")).where(Booking.packages_price_id == id_package_price))).one()._asdict()

    findUser = (await session.execute(select(Booking).options(joinedload(Booking.user)).where(Booking.packages_price_id == id_package_price,Booking.status != BookingStatusEnum.CANCELLED))).scalars().all()

    return {
        "msg" : "success",
        "data" : {
            "count_filled" : getStatistikBooking["count_filled"],
            "count_booking" : getStatistikBooking["count_booking"],
            "count_available" : findPackagePrice.seat_count - (getStatistikBooking["count_filled"] + getStatistikBooking["count_booking"]),
            "user" : [user.user for user in findUser]
        }
    }

# rating
async def getPackageRating(id_package : int,session:AsyncSession) -> GetPackageRatingResponse:
    getStatistikRating = (await session.execute(select(func.count(Rating.id).label("count_rating"),func.count(Rating.id).filter(Rating.review != None).label("count_reviews"),func.avg(Rating.rating).label("avg_rating"),func.count(Rating.id).filter(Rating.rating == 5).label("count_5"),func.count(Rating.id).filter(Rating.rating == 4).label("count_4"),func.count(Rating.id).filter(Rating.rating == 3).label("count_3"),func.count(Rating.id).filter(Rating.rating == 2).label("count_2"),func.count(Rating.id).filter(Rating.rating == 1).label("count_1")))).one()

    findReviews = (await session.execute(select(Rating).options(joinedload(Rating.user)).where(and_(Rating.package_id == id_package,Rating.review != None)))).scalars().all()

    return {
        "msg" : "success",
        "data" : {
            "statistik" : getStatistikRating,
            "reviews" : findReviews
        }
    }

async def addRating(user: dict,rating : AddRatingRequest,session : AsyncSession) -> RatingWithUserPackage:
    findpackage = (await session.execute(select(Package).where(Package.id == rating.package_id))).scalar_one_or_none()

    if not findpackage :
        raise HttpException(404,"package is not found")
    
    ratingMapping = rating.model_dump()
    ratingMapping.update({"id" : generate_id(),"user_id" : user["id"],"create_at" : datetime.now()})

    packageDictCopy = deepcopy(findpackage.__dict__)
    session.add(Rating(**ratingMapping))
    await session.commit()

    return {
        "msg" : "success",
        "data" : {
            **ratingMapping,
            "package" : packageDictCopy,
            "user" : user
        }
    }

async def updateRating(user : dict,id_rating : int,rating : UpdateRatingRequest,session : AsyncSession) -> RatingBase :
    findRating = (await session.execute(select(Rating).where(and_(Rating.id == id_rating,Rating.user_id == user["id"])))).scalar_one_or_none()

    if findRating is None :
        raise HttpException(404,"rating is not found")

    updateTable(rating,findRating)
    ratingDictCopy = deepcopy(findRating.__dict__)
    await session.commit()

    return {
        "msg" : "success",
        "data" : ratingDictCopy
    }

async def deleteRating(user : dict,id_rating : int,session : AsyncSession) -> RatingBase :
    findRating = (await session.execute(select(Rating).where(and_(Rating.id == id_rating,Rating.user_id == user["id"])))).scalar_one_or_none()

    if findRating is None :
        raise HttpException(404,"rating is not found")

    ratingDictCopy = deepcopy(findRating.__dict__)
    await session.delete(findRating)
    await session.commit()

    return {
        "msg" : "success",
        "data" : ratingDictCopy
    }
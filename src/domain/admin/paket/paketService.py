from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,and_
from fastapi import UploadFile
from sqlalchemy.orm import joinedload, subqueryload
# models
from ....models.package_model import Package,PackagePrices,GalleryPackage, Booking, Rating
from ....models.user_model import User

# schemas
from .paketSchema import AddPackageRequest,AddPackagePricesRequest, GetAllPackagesQuery, UpdatePackageRequest,UpdatePackagePricesRequest,ResponsePaketPag, GetPackageRatingResponse
from ...schemas.package_schema import PackageBase,PackageWithPrices,PackageWithGallery,GalleryPackageBase, PackagePricesBase, PackageWithPricesGalleryUser

# types
from ....types.package_types import BookingStatusEnum 

# common
import aiofiles
from copy import deepcopy
import math
from ....error.errorHandling import HttpException
from ....utils.generateId_util import generate_id
import os
from ....utils.updateTable_util import updateTable
from multiprocessing import Process

IMAGE_PACKAGE_STORE = os.getenv("IMAGE_PACKAGE_BASE_STORE")
IMAGE_PACKAGE_BASE_URL = os.getenv("IMAGE_PACKAGE_BASE_URL")
# package
async def addPackage(admin : dict, package : AddPackageRequest,session : AsyncSession) -> PackageBase:
    packageMapping = package.model_dump(exclude={"image"})
    packageMapping.update({"id" : generate_id(),"add_by_admin" : admin["id"]})

    ext_file = package.image.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{generate_id()}-{package.image.filename.split(' ')[0].split('.')[0]}.{ext_file[-1]}"
    file_name_save = f"{IMAGE_PACKAGE_STORE}{file_name}"

    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(package.image.file.read())
        packageMapping["image"] = f"{IMAGE_PACKAGE_BASE_URL}/{file_name}"

    session.add(Package(**packageMapping))
    await session.commit()
    return {
        "msg" : "success",
        "data" : packageMapping
    }

async def updatePackage(admin : dict, id_package : int,request : UpdatePackageRequest,session:AsyncSession) -> PackageBase:
    findPackage = (await session.execute(select(Package).where(and_(Package.id == id_package,Package.add_by_admin == admin["id"])))).scalar_one_or_none()
    if not findPackage :
        raise HttpException(404,f"package not found")

    if request.model_dump(exclude_none=True,exclude={"image"}) :
        updateTable(request.model_dump(exclude={"image"}),findPackage)

    if request.image :
        ext_file = request.image.filename.split(".")
        if ext_file[-1] not in ["jpg","png","jpeg"] :
            raise HttpException(400,f"file harus berupa gambar")

        file_name = f"{generate_id()}-{request.image.filename.split(' ')[0]}.{ext_file[-1]}"
        file_name_save = f"{IMAGE_PACKAGE_STORE}{file_name}"
        file_name_before = findPackage.image.split("/")[-1]

        async with aiofiles.open(file_name_save, "wb") as f:
            await f.write(request.image.file.read())
            findPackage.image = f"{IMAGE_PACKAGE_BASE_URL}/{file_name}" 

    packageDictCopy = deepcopy(findPackage.__dict__)
    await session.commit()
    if findPackage.image :
        remoove_image_process = Process(target=os.remove, args=(f"{IMAGE_PACKAGE_STORE}{file_name_before}",))
        remoove_image_process.start()

    return {
        "msg" : "success",
        "data" : packageDictCopy
    }
    
async def deletePackage(admin: dict, id_package : int,session:AsyncSession) -> PackageBase:
    findPackage = (await session.execute(select(Package).where(and_(Package.id == id_package,Package.add_by_admin == admin["id"])))).scalar_one_or_none()
    if not findPackage :
        raise HttpException(404,f"package not found")

    packageDictCopy = deepcopy(findPackage.__dict__)
    await session.delete(findPackage)
    await session.commit()
    return {
        "msg" : "success",
        "data" : packageDictCopy
    }

async def getAllPackage(admin : dict,query : GetAllPackagesQuery,session:AsyncSession) -> list[PackageBase] | ResponsePaketPag:
    statementSelectPackage = select(Package).where(and_(Package.add_by_admin == admin["id"],Package.departure_date >= query.start_date if query.start_date else True,Package.departure_date <= query.end_date if query.end_date else True,Package.name.like(f"%{query.name}%") if query.name else True))

    if query.page :
        findPackage = (await session.execute(statementSelectPackage.limit(10).offset(10 * (query.page - 1)))).scalars().all()
        conntData = (await session.execute(func.count(Package.id))).scalar_one()
        countPage = math.ceil(conntData / 10)
        return {
            "msg" : "success",
            "data" : {
                "data" : findPackage,
                "count_data" : len(findPackage),
                "count_page" : countPage
            }
        }
    else :
        findPackage = (await session.execute(statementSelectPackage)).scalars().all()
        print(findPackage)
        return {
            "msg" : "success",
            "data" : findPackage
        }

async def getPackageById(admin : dict,id_package : int,session:AsyncSession) -> PackageWithPricesGalleryUser:
    findPackage = (await session.execute(select(Package).options(subqueryload(Package.package_prices),subqueryload(Package.gallery)).where(and_(Package.id == id_package, Package.add_by_admin == admin["id"])))).scalar_one_or_none()

    if not findPackage :
        raise HttpException(404,f"package not found")

    findUser = (await session.execute(select(User).where(User.booking.any(Booking.package_id == findPackage.id,Booking.status != BookingStatusEnum.CANCELLED)))).scalars().all()

    return {
        "msg" : "success",
        "data" : {
            **findPackage.__dict__,
            "user" : findUser
        }
    }


# package prices
async def addPackagePrices(admin : dict, packagePrices:AddPackagePricesRequest,session:AsyncSession) -> PackageWithPrices:
    findPackage = (await session.execute(select(Package).where(and_(Package.id == packagePrices.package_id,Package.add_by_admin == admin["id"])))).scalar_one_or_none()
    if not findPackage :
        raise HttpException(404,f"paket tidak ditemukan")

    packagePricesDb = []
    packagePriceResponse = []
    for packagePrice in packagePrices.package_prices :
        findPackagePrice = (await session.execute(select(PackagePrices).where(and_(PackagePrices.package_id == findPackage.id,PackagePrices.package_type == packagePrice.package_type,PackagePrices.room_type == packagePrice.room_type)))).scalar_one_or_none()

        if findPackagePrice :
            raise HttpException(400,f"Paket price with package type {packagePrice.package_type.value} and room type {packagePrice.room_type.value} already exists")
       
        packagePriceMapping = packagePrice.model_dump()
        packagePriceMapping.update({"id" : generate_id(),"package_id" : findPackage.id})
        packagePricesDb.append(PackagePrices(**packagePriceMapping))
        packagePriceResponse.append(packagePriceMapping)
    
    packageDictCopy = deepcopy(findPackage.__dict__)
    session.add_all(packagePricesDb)
    await session.commit()
    return {
        "msg" : "success",
        "data" : {
            **packageDictCopy,
            "package_prices" : packagePriceResponse
        }
    }

async def updatePackagePrices(admin : dict,id_package_prices : int,request : UpdatePackagePricesRequest,session:AsyncSession) -> PackagePricesBase:
    findPackagePrices = (await session.execute(select(PackagePrices).where(and_(PackagePrices.id == id_package_prices,Package.add_by_admin == admin["id"])))).scalar_one_or_none()
    if not findPackagePrices :
        raise HttpException(404,f"package prices not found")
    
    validationPackagePrice = (await session.execute(select(PackagePrices).where(and_(PackagePrices.id != id_package_prices,PackagePrices.package_id == findPackagePrices.package_id,PackagePrices.package_type == (request.package_type if request.package_type else findPackagePrices.package_type),PackagePrices.room_type == (request.room_type if request.room_type else findPackagePrices.room_type))))).scalar_one_or_none()

    if validationPackagePrice :
        raise HttpException(400,f"Paket price with package type {validationPackagePrice.package_type} and room type {validationPackagePrice.room_type} already exists")

    updateTable(request.model_dump(exclude_none=True),findPackagePrices)
    packageDictCopy = deepcopy(findPackagePrices.__dict__)
    await session.commit()
    return {
        "msg" : "success",
        "data" : packageDictCopy
    }

async def deletePackagePrices(id_package_prices : int,session:AsyncSession) -> PackagePricesBase:
    findPackagePrices = (await session.execute(select(PackagePrices).where(PackagePrices.id == id_package_prices))).scalar_one_or_none()
    if not findPackagePrices :
        raise HttpException(404,f"package prices not found")

    packageDictCopy = deepcopy(findPackagePrices.__dict__)
    await session.delete(findPackagePrices)
    await session.commit()
    return {
        "msg" : "success",
        "data" : packageDictCopy
    }



# package gallery
async def addGalleryPackage(admin : dict, id_package : int,file : UploadFile,session:AsyncSession) -> PackageWithGallery:
    findPackage = (await session.execute(select(Package).where(and_(Package.id == id_package,Package.add_by_admin == admin["id"])))).scalar_one_or_none()
    if not findPackage :
        raise HttpException(404,f"paket tidak ditemukan")
    
    ext_file = file.filename.split(".")

    if ext_file[-1] not in ["jpg","png","jpeg"] :
        raise HttpException(400,f"file harus berupa gambar")

    file_name = f"{generate_id()}-{file.filename.split(' ')[0].split('.')[0]}.{ext_file[-1]}"
    file_name_save = f"{IMAGE_PACKAGE_STORE}{file_name}"
    galleryPackageMapping = {}
    packageDictCopy = deepcopy(findPackage.__dict__)   
    async with aiofiles.open(file_name_save, "wb") as f:
        await f.write(file.file.read())
        galleryPackageMapping = {
            "id" : generate_id(),
            "package_id" : id_package,
            "image" : f"{IMAGE_PACKAGE_BASE_URL}/{file_name}"
        }
        session.add(GalleryPackage(**galleryPackageMapping))
        await session.commit()
    return {
        "msg" : "success",
        "data" : {
            **packageDictCopy,
            "gallery" : [galleryPackageMapping]
        }
    }

async def deleteGalleryPackage(id_gallery_package : int,session:AsyncSession) -> GalleryPackageBase:
    findGalleryPackage = (await session.execute(select(GalleryPackage).where(GalleryPackage.id == id_gallery_package))).scalar_one_or_none()
    if not findGalleryPackage :
        raise HttpException(404,f"gallery package not found")
    
    file_name_before = findGalleryPackage.image.split("/")[-1]

    packageDictCopy = deepcopy(findGalleryPackage.__dict__)
    await session.delete(findGalleryPackage)
    await session.commit()

    remoove_image_process = Process(target=os.remove, args=(f"{IMAGE_PACKAGE_STORE}{file_name_before}",))
    remoove_image_process.start()

    return {
        "msg" : "success",
        "data" : packageDictCopy
    }

# rating
async def getPackageRating(admin : dict, id_package : int,session:AsyncSession) -> GetPackageRatingResponse:
    getStatistikRating = (await session.execute(select(func.count(Rating.id).label("count_rating"),func.count(Rating.id).filter(Rating.review != None).label("count_reviews"),func.avg(Rating.rating).label("avg_rating"),func.count(Rating.id).filter(Rating.rating == 5).label("count_5"),func.count(Rating.id).filter(Rating.rating == 4).label("count_4"),func.count(Rating.id).filter(Rating.rating == 3).label("count_3"),func.count(Rating.id).filter(Rating.rating == 2).label("count_2"),func.count(Rating.id).filter(Rating.rating == 1).label("count_1")).where(and_(Package.id == id_package, Package.add_by_admin == admin["id"])))).one()

    findReviews = (await session.execute(select(Rating).options(joinedload(Rating.user)).where(and_(Rating.package_id == id_package,Rating.review != None)))).scalars().all()

    return {
        "msg" : "success",
        "data" : {
            "statistik" : getStatistikRating,
            "reviews" : findReviews
        }
    }
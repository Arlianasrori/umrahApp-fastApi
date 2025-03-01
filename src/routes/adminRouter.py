from fastapi import APIRouter, Depends, UploadFile
# auth_profile
from ..domain.admin.auth_profile import authProfileService 

# package
from ..domain.admin.paket import paketService
from ..domain.admin.paket.paketSchema import AddPackageRequest,AddPackagePricesRequest, GetAllPackagesQuery, UpdatePackageRequest,UpdatePackagePricesRequest, ResponsePaketPag, GetPackageRatingResponse
from ..domain.schemas.package_schema import PackageBase,PackageWithPrices,PackageWithGallery, GalleryPackageBase, PackagePricesBase, PackageWithPricesGalleryUser

# booking
from ..domain.admin.booking import bookingService
from ..domain.admin.booking.bookingSchema import GetPackageContainsBookingResponsePag,GetPackageContainsBooking,GetAllPackagesQuery as GetAllPackagesBookingQuery,UpdateBookingStatusRequest
from ..domain.schemas.package_schema import PackageWithBooking, BookingWithUserPrice

# db
from ..db.sessionDepedency import sessionDepedency
# schemas
from ..domain.schemas.response_schema import ApiResponse,MessageOnlyResponse
from ..domain.schemas.user_schema import UserBase
# depends
from ..auth.auth_depends.admin.depend_auth_admin import adminAuth
from ..auth.auth_depends.admin.get_admin_auth import getAdminAuth


adminRouter = APIRouter(prefix="/admin",dependencies=[Depends(adminAuth)])

# auth_profile
@adminRouter.get("/",response_model=ApiResponse[UserBase],tags=["ADMIN"])
async def get_admin(admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await authProfileService.getAdmin(admin["id"],session)

# package
@adminRouter.post("/package",response_model=ApiResponse[PackageBase],tags=["ADMIN/PACKAGE"])
async def add_package(request : AddPackageRequest = Depends(AddPackageRequest.as_form),admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.addPackage(admin,request,session)

@adminRouter.get("/package",response_model=ApiResponse[list[PackageBase] | ResponsePaketPag],tags=["ADMIN/PACKAGE"])
async def get_all_package(query : GetAllPackagesQuery = Depends(),admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.getAllPackage(admin,query,session)

@adminRouter.get("/package/{id_package}",response_model=ApiResponse[PackageWithPricesGalleryUser],tags=["ADMIN/PACKAGE"])
async def get_package_by_id(id_package : int,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.getPackageById(admin,id_package,session)

@adminRouter.put("/package/{id_package}",response_model=ApiResponse[PackageBase],tags=["ADMIN/PACKAGE"])
async def update_package(id_package : int,request : UpdatePackageRequest,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.updatePackage(admin,id_package,request,session)

@adminRouter.delete("/package/{id_package}",response_model=ApiResponse[PackageBase],tags=["ADMIN/PACKAGE"])
async def delete_package(id_package : int,session : sessionDepedency) :
    return await paketService.deletePackage(id_package,session)

# package prices
@adminRouter.post("/package/prices",response_model=ApiResponse[PackageWithPrices],tags=["ADMIN/PACKAGE-PRICES"])
async def add_package_prices(request : AddPackagePricesRequest,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.addPackagePrices(admin,request,session)

@adminRouter.put("/package/prices/{id_package_prices}",response_model=ApiResponse[PackagePricesBase],tags=["ADMIN/PACKAGE-PRICES"])
async def update_package_prices(id_package_prices : int,request : UpdatePackagePricesRequest,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.updatePackagePrices(admin,id_package_prices,request,session)

@adminRouter.delete("/package/prices/{id_package_prices}",response_model=ApiResponse[PackagePricesBase],tags=["ADMIN/PACKAGE-PRICES"])
async def delete_package_prices(id_package_prices : int,session : sessionDepedency) :
    return await paketService.deletePackagePrices(id_package_prices,session)

# package gallery
@adminRouter.post("/package/gallery/{id_package}",response_model=ApiResponse[PackageWithGallery],tags=["ADMIN/GALLERY"])
async def add_package_gallery(id_package : int,image : UploadFile,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.addGalleryPackage(admin,id_package,image,session)

@adminRouter.delete("/package/gallery/{id_gallery_package}",response_model=ApiResponse[GalleryPackageBase],tags=["ADMIN/GALLERY"])
async def delete_package_gallery(id_gallery_package : int,session : sessionDepedency) :
    return await paketService.deleteGalleryPackage(id_gallery_package,session)

# booking
@adminRouter.get("/booking/package/contains-booking",response_model=ApiResponse[list[GetPackageContainsBooking] | GetPackageContainsBookingResponsePag],tags=["ADMIN/BOOKING"])
async def get_all_package_contains_booking(query : GetAllPackagesBookingQuery = Depends(),admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await bookingService.getAllPackageContainsBooking(admin,query,session)

@adminRouter.get("/booking/{id_package}",response_model=ApiResponse[PackageWithBooking],tags=["ADMIN/BOOKING"])
async def get_booking_detail(id_package : int,session : sessionDepedency) :
    return await bookingService.getDetailBooking(id_package,session)

@adminRouter.patch("/booking/status/{id_booking}",response_model=ApiResponse[BookingWithUserPrice],tags=["ADMIN/BOOKING"])
async def update_booking_status(id_booking : int,request : UpdateBookingStatusRequest,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await bookingService.updateBookingStatus(admin,id_booking,request,session)

# rating
@adminRouter.get("/package/rating/{id_package}",response_model=ApiResponse[GetPackageRatingResponse],tags=["ADMIN/RATING"])
async def get_all_package_contains_booking(id_package : int,admin : dict = Depends(getAdminAuth),session : sessionDepedency = None) :
    return await paketService.getPackageRating(admin,id_package,session)
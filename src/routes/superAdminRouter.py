from fastapi import APIRouter, Depends, UploadFile
# service
from ..domain.super_admin import superAdminService

# db
from ..db.sessionDepedency import sessionDepedency
# schemas
from ..domain.super_admin.superAdminSchema import AddAdminRequest,UpdateAdminRequest
from ..domain.schemas.response_schema import ApiResponse,MessageOnlyResponse
from ..domain.schemas.user_schema import UserBase
# depends
from ..auth.auth_depends.super_admin.depend_auth_super_admin import superAdminAuth
from ..auth.auth_depends.super_admin.get_super_admin_auth import getSuperAdminAuth


superAdminRouter = APIRouter(prefix="/super-admin",dependencies=[Depends(superAdminAuth)])

# auth_profile
@superAdminRouter.get("/",response_model=ApiResponse[UserBase],tags=["SUPERADMIN"])
async def get_super_admin(superAdmin : dict = Depends(getSuperAdminAuth),session : sessionDepedency = None) :
    return await superAdminService.getSuperAdmin(superAdmin["id"],session)

# admin
@superAdminRouter.post("/admin",response_model=ApiResponse[UserBase],tags=["SUPERADMIN"])
async def add_admin(admin : AddAdminRequest = Depends(AddAdminRequest.as_form),session : sessionDepedency = None) :
    return await superAdminService.addAdmin(admin,session)

@superAdminRouter.get("/admin",response_model=ApiResponse[list[UserBase]],tags=["SUPERADMIN"])
async def get_all_admin(session : sessionDepedency = None) :
    return await superAdminService.getAllAdmin(session)

@superAdminRouter.get("/admin/{id_admin}",response_model=ApiResponse[UserBase],tags=["SUPERADMIN"])
async def get_admin_by_id(id_admin : int,session : sessionDepedency = None) :
    return await superAdminService.getAdminById(id_admin,session)

@superAdminRouter.put("/admin/{id_admin}",response_model=ApiResponse[UserBase],tags=["SUPERADMIN"])
async def update_admin(id_admin : int,admin : UpdateAdminRequest = Depends(UpdateAdminRequest.as_form),session : sessionDepedency = None) :
    return await superAdminService.updateAdmin(id_admin,admin,session)

@superAdminRouter.delete("/admin/{id_admin}",response_model=ApiResponse[UserBase],tags=["SUPERADMIN"])
async def delete_admin(id_admin : int,session : sessionDepedency) :
    return await superAdminService.deleteAdmin(id_admin,session)

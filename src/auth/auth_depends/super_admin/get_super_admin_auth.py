from fastapi import Request

async def getSuperAdminAuth(req : Request) :
    return req.superAdmin
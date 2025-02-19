from fastapi import Request

async def getAdminAuth(req : Request) :
    return req.admin
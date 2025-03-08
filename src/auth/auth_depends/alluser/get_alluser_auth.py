from fastapi import Request

async def getAllUserAuth(req : Request) :
    return req.allUser
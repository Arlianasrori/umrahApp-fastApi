from fastapi import Request

async def getUsetAuth(req : Request) :
    return req.User
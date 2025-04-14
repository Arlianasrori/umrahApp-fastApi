from fastapi import Request

async def getUserAuth(req : Request) :
    return req.User
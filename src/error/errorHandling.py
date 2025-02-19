from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError,ResponseValidationError
from fastapi.encoders import jsonable_encoder


class HttpException(Exception) :
    def __init__(self, status : int,message : str) -> None:
        self.status = status
        self.messsage = message

def add_exception_server(App : FastAPI) :
    @App.exception_handler(HttpException)
    async def handlingHttpException(request: Request, exc: HttpException):
        return JSONResponse(
            status_code=exc.status,
            content={"msg" : exc.messsage},
        )

    @App.exception_handler(Exception)
    def handlingExceptionError(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({"msg" : exc.args}),
        )

    # @App.exception_handler(RequestValidationError)
    # async def validation_exception_handler(request, exc : RequestValidationError):
    #     return JSONResponse(
    #         status_code=400,
    #         content={"msg" : exc.args[0][0]["msg"]},
    #     )
    # @App.exception_handler(ResponseValidationError)
    # async def validation_exception_handler(request, exc : ResponseValidationError):
    #     print(exc.__dict__["_errors"][0]["msg"])
    #     return JSONResponse(
    #         status_code=400,
    #         content={"msg" : exc.__dict__["_errors"][0]["msg"]},
    #     )
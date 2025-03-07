# Import required modules
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(f"{os.getcwd()}/.env")

# Import models from src module
from src.models import *

# Import error handling function
from src.error.errorHandling import add_exception_server

# Import routers
from src.routes.authRouter import authRouter
from src.routes.adminRouter import adminRouter
from src.routes.userRouter import userRouter
from src.routes.superAdminRouter import superAdminRouter

# socket
from src.socket.socket import socket_app
from src.socket.socket_connection_handling import handle_socket_connection

# Initialize FastAPI application with configuration
App = FastAPI(
    title="API SPEC FOR PRESISI APP",
    description="This is the API specification for absensi App, it can be your guide in consuming the API. Please pay attention to the required fields in this API specification",
    servers=[{"url": "http://localhost:2008", "description": "development server"}],
    contact={"name": "Habil Arlian Asrori", "email": "arlianasrori@gmail.com"}
)

# Add routers to the application
routes = [authRouter,superAdminRouter,adminRouter,userRouter]
for router in routes:
    App.include_router(router)

# Configure CORS middleware
origins = [
    "http://localhost:3000"
]

App.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for public files
App.mount("/public", StaticFiles(directory="src/public"), name="public")

# mount socket app
App.mount("/socket",app=socket_app)

# Add error handling to the application
add_exception_server(App)

# running handle socket connection
handle_socket_connection()

# Function to run the server
async def runServer():
    config = uvicorn.Config("main:App", port=2008, reload=True)
    server = uvicorn.Server(config)
    await server.serve()
    
# Run the server if the script is executed directly
if __name__ == "__main__":
    # run handle connect and disconect event socket
    # asyncio.run(connetDisconnectSocket())
    # run server
    asyncio.run(runServer())
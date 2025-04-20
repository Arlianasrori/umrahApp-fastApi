from .socket_auth_middleware import socket_auth_middleware
from .socket_error_handling import socketError
from .socket import sio

# users active
online_users = {}


def handle_socket_connection() :
    # handle when client connect to socket
    @sio.on("connect")
    async def connect(sid, environ,auth):
        print(f"ini auth {auth}")
        # Melakukan autentikasi pengguna
        auth = await socket_auth_middleware(auth)
        if not auth:
            # Mengembalikan error jika autentikasi gagal
            await socketError(401,"Unauthorized","Unauthorized",sid)
            return False

        print(auth)

        user_id = auth["id_user"]
        print("connect")
        # Menyimpan informasi pengguna yang baru terhubung
        online_users[sid] = {
            "user_id" : user_id
        }

    # handle when client disconncet to socket
    @sio.on("disconnect")
    async def disconnect(sid):
        user = online_users.get(sid)
        if user :
            # Menghapus pengguna dari daftar online
            del online_users[sid]
            print("disconnect")

async def getUserSid(user_id : int) -> int | None :
    print(online_users)
    # Looping untuk setiap pengguna online
    for user in online_users.items():
        sid, user = user

        # Memeriksa apakah user_id sama dengan id_user
        if user["user_id"] == user_id :
            return sid
    
    return None
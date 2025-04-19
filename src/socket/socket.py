import socketio

sio = socketio.AsyncServer(cors_allowed_origins='*',  async_mode='asgi', async_handlers=True)
socket_app = socketio.ASGIApp(sio)
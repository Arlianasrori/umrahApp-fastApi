import socketio

sio = socketio.AsyncServer(cors_allowed_origins='http://localhost:3000', cors_credentials=False, transports=['polling', 'websocket'], async_mode='asgi', async_handlers=True)
socket_app = socketio.ASGIApp(sio)
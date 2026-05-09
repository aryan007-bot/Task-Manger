"""
SocketIO event handlers — real-time task broadcasting on the /tasks namespace.
"""
from flask_socketio import join_room, emit
from flask import request
from app.extensions import socketio


@socketio.on("connect", namespace="/tasks")
def on_connect():
    emit("connected", {"message": "Connected to task updates."})


@socketio.on("disconnect", namespace="/tasks")
def on_disconnect():
    pass


@socketio.on("join", namespace="/tasks")
def on_join(data: dict):
    room: str = data.get("room", "global")
    join_room(room)
    emit("joined", {"room": room})


@socketio.on("ping", namespace="/tasks")
def on_ping():
    emit("pong", {"message": "pong"})

from flask import Flask,render_template, request #Web framework for handling HTTP requests.
from flask_socketio import SocketIO, emit #Enables real-time WebSocket communication.
import random

app = Flask(__name__)
socketio = SocketIO(app)

users={}#all the user data key: socketid value : username and avatar_url

@app.route('/')
def index():
    return render_template('index.html')

#  Socket.IO Event: connect Triggered when a new client connects via WebSocket.
@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000,9999)}"                                 
    gender = random.choice(["girl", "boy"])
    #https://avatar.iran.liara.run/public/boy?username
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"

    users[request.sid] = {
        "username": username,
        "avatar": avatar_url,
        "gender": gender 
    }

    # emit() to send real-time events from the server to connected clients
    emit("user_joined", {
        "username": username,
        "avatar": avatar_url,
        "gender": gender
    }, broadcast=True)

    emit("set_username", {
        "username": username,
        "gender": gender
    })

@socketio.on("disconnect")
def handleDisconnect():
    #request.sid is generated automatically by Flask-SocketIO
    user = users.pop(request.sid, None)

    if user: 
        emit("user_left",{"username": user["username"]}, broadcast=True)

@socketio.on("send_message")
def handle_message(data):
    #data is a dictionary with the message and the sender's username 
    user = users.get(request.sid)
    if user:
        emit("new_message",{
            "username": user["username"],
            "avatar": user["avatar"],
            "message":data["message"]
        }, broadcast=True)

@socketio.on("update_profile")
def handle_update_profile(data):
    user = users.get(request.sid)
    if user:
        old_username = user["username"]
        new_username = data.get("username", old_username)
        new_gender = data.get("gender", user["gender"])
        
        # Update user data
        user["username"] = new_username
        user["gender"] = new_gender
        user["avatar"] = f"https://avatar.iran.liara.run/public/{new_gender}?username={new_username}"
        
        # Notify all clients
        emit("profile_updated", {
            "old_username": old_username,
            "new_username": new_username,
            "gender": new_gender,
            "avatar": user["avatar"]
        }, broadcast=True)
# starts the server
if __name__ == "__main__":
    socketio.run(app) 
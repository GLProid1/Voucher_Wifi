from app.app import create_app
from app.extensions import socketio

app = create_app()

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")
    
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5500, debug=True)

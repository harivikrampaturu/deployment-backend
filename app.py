from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from uuid import uuid4
from datetime import datetime, timezone
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

# Mock databases
projects_db = []
resources_db = []
allocations_db = []
notifications_db = []
chat_messages_db = []
tasks_db = []

# Copy all your existing routes here
# ... existing code ...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    socketio.run(app, host='0.0.0.0', port=port) 
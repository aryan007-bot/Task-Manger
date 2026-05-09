"""
Application entry point.
For production, use: gunicorn -k eventlet -w 1 -b 0.0.0.0:$PORT "run:app"
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    socketio.run(app, host="0.0.0.0", port=port, debug=debug, use_reloader=False)

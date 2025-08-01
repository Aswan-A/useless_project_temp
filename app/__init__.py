from flask import Flask
from app.routes import register_blueprints
import threading
from app.utils.cleanup import delete_old_files
from flask_cors import CORS

def create_app():
    app =Flask(__name__, static_folder='static', static_url_path='/static')
    CORS(app) 
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1 GB
    threading.Thread(target=delete_old_files, daemon=True).start()
    register_blueprints(app)

    return app

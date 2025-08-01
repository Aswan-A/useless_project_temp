from .upload import upload_bp
from .yt import yt_bp
from .link import link_bp

def register_blueprints(app):
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(yt_bp, url_prefix='/api/yt')
    app.register_blueprint(link_bp, url_prefix='/api/link')


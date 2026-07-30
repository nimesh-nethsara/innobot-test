# from flask import Flask
# from app.config import Config
# from app.extensions import db
# from app.utils.errors import register_error_handlers

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     # Initialize DB extension
#     db.init_app(app)

#     # Register Global Error Handlers
#     register_error_handlers(app)

#     # Register Blueprints
#     from app.routes.auth import auth_bp
#     from app.routes.doctors import doctors_bp
#     from app.routes.appointments import appointments_bp

#     app.register_blueprint(auth_bp)
#     app.register_blueprint(doctors_bp)
#     app.register_blueprint(appointments_bp)

#     return app

from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db
from app.utils.errors import register_error_handlers

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend requests
    CORS(app)

    # Initialize extensions
    db.init_app(app)

    # Register error handlers
    register_error_handlers(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.doctors import doctors_bp
    from app.routes.appointments import appointments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)

    return app
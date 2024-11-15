#!/usr/bin/python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from os import getenv
from datetime import timezone, timedelta


local_timezone = timezone(timedelta(hours=2))

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(get_remote_address, default_limits=["200 per day", "50 per hour"])
bcrypt = Bcrypt()
swagger = Swagger()

def create_app():
    app = Flask(__name__)


    DB_USER = getenv(DB_USER)
    DB_PASSWORD = getenv(DB_PASSWORD)
    DB_HOST = getenv(DB_HOST)
    DB_NAME = getenv(DB_NAME)
    SECRET_KEY = getenv(SECRET_KEY)

    # Configure the app (set database URI, secret key, etc.)

    # app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    app.config['SECRET_KEY'] = f"{SECRET_KEY}"

    # Initialize the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)
    bcrypt.init_app(app)
    swagger.init_app(app)


    from app.models.user import User
    from app.models.role import Role
    from app.models.language import Language
    from app.models.reset_token import ResetToken
    from app.models.group import Group
    from app.models.user_group import UserGroup
    from app.models.session import Session
    from app.models.user_session import UserSession
    from app.models.package import Package
    from app.models.user_package import UserPackage

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # import Blueprints
    from app.views.auth.auth import auth
    from app.views.auth.profile import profile

    # Register blueprints
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(profile, url_prefix="/profile")

    return app

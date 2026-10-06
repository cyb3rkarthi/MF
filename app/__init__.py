import os
from flask import Flask
from dotenv import load_dotenv
from .db import get_database

load_dotenv()


def create_app(test_config=None):
    """
    Application factory for Madras Foodies Consultancy web application.
    Configures secret key, sets up database connection (MongoDB Atlas with
    SQLite fallback), and registers page & API routes blueprint.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    if test_config:
        app.config.update(test_config)

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB", "madras_foodies")

    db, db_type = get_database(mongo_uri, db_name)
    app.extensions["db"] = db
    app.extensions["db_type"] = db_type

    from .routes import main
    app.register_blueprint(main)

    return app


__all__ = ["create_app"]


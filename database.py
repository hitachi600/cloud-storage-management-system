import os
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy extension
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the Flask application.
    Creates all tables if they do not exist.
    """
    # Ensure instance or db folder exists if using sqlite
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        db_path_str = db_uri.replace('sqlite:///', '')
        if db_path_str and db_path_str != ':memory:':
            db_path = Path(db_path_str)
            db_path.parent.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        # Import models so SQLAlchemy discovers them before creating tables
        from models.user import User
        from models.file import FileRecord
        db.create_all()

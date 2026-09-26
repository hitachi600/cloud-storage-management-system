"""
Pytest configuration and shared fixtures for Cloud Storage Management System.
"""

import sys
import pytest
import shutil
import tempfile
from pathlib import Path

# Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from config import TestConfig
from database import db
from models.user import User
from models.file import FileRecord


@pytest.fixture
def app():
    """Create a new application instance for a test."""
    temp_dir = tempfile.mkdtemp()
    TestConfig.UPLOAD_FOLDER = Path(temp_dir)

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    # Clean up temp folder
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Create and return a sample registered user."""
    with app.app_context():
        user = User(name="Test Student", email="student@university.edu")
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()
        user_dto = type('UserDTO', (), {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'password': 'SecurePass123!'
        })()
        return user_dto

"""
Configuration Module for Cloud Storage Management System.
Handles loading environment variables and configuring Flask, Database, and Storage settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if it exists
dotenv_path = BASE_DIR / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)


class Config:
    """Base application configuration class."""

    # Security & Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key-replace-in-production')

    # Environment
    ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') in ('1', 'true', 'True')

    # Ensure instance directory exists
    instance_dir = BASE_DIR / 'instance'
    instance_dir.mkdir(parents=True, exist_ok=True)

    # Database Configuration
    # Defaults to SQLite in instance/ directory. Can be configured for AWS RDS (PostgreSQL/MySQL)
    default_sqlite_path = (instance_dir / 'cloud_storage.db').as_posix()
    raw_db_uri = os.environ.get('DATABASE_URI', '')
    if not raw_db_uri or raw_db_uri == 'sqlite:///instance/cloud_storage.db':
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{default_sqlite_path}"
    else:
        SQLALCHEMY_DATABASE_URI = raw_db_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Storage Mode: 'local' (development) or 's3' (AWS S3)
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'local').strip().lower()

    # Local Storage Upload Folder
    UPLOAD_FOLDER = BASE_DIR / os.environ.get('UPLOAD_FOLDER', 'uploads')

    # Upload Limits (Default 16 MB)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

    # Allowed File Extensions
    ALLOWED_EXTENSIONS = set(
        ext.strip().lower()
        for ext in os.environ.get(
            'ALLOWED_EXTENSIONS',
            'pdf,jpg,jpeg,png,txt,docx,csv,xlsx,zip'
        ).split(',')
        if ext.strip()
    )

    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME', '')

    @classmethod
    def validate_storage_config(cls):
        """Validate storage configuration on startup."""
        if cls.STORAGE_TYPE == 's3':
            missing_vars = []
            if not cls.AWS_ACCESS_KEY_ID:
                missing_vars.append('AWS_ACCESS_KEY_ID')
            if not cls.AWS_SECRET_ACCESS_KEY:
                missing_vars.append('AWS_SECRET_ACCESS_KEY')
            if not cls.AWS_S3_BUCKET_NAME:
                missing_vars.append('AWS_S3_BUCKET_NAME')
            if missing_vars:
                print(f"[WARNING] AWS S3 is selected but missing variables: {', '.join(missing_vars)}. "
                      f"Storage operations may fail until credentials are provided.")
        elif cls.STORAGE_TYPE == 'local':
            # Ensure local uploads directory exists
            cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            print(f"[INFO] Using Local Storage mode. Uploads directory: {cls.UPLOAD_FOLDER}")


class TestConfig(Config):
    """Configuration class for automated testing."""
    TESTING = True
    DEBUG = True
    STORAGE_TYPE = 'local'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

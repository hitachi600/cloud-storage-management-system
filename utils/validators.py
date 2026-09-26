"""
Validation and utility helper functions for Cloud Storage Management System.
"""

import re
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename


# Standard email regex pattern
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if the file has an approved extension.
    Example: 'report.pdf' -> True if 'pdf' in allowed_extensions
    """
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def get_file_extension(filename: str) -> str:
    """Extract lowercase file extension."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return 'unknown'


def sanitize_filename(filename: str) -> tuple[str, str]:
    """
    Sanitize the uploaded filename and generate a collision-free stored filename.
    Returns:
        (original_clean_filename, unique_stored_filename)
    """
    clean_name = secure_filename(filename)
    if not clean_name:
        clean_name = f"file_{uuid.uuid4().hex[:8]}"

    ext = get_file_extension(clean_name)
    unique_prefix = uuid.uuid4().hex
    stored_filename = f"{unique_prefix}_{clean_name}"
    return clean_name, stored_filename


def format_bytes(bytes_val: int) -> str:
    """
    Format byte integer to human-friendly string.
    Example: 1048576 -> '1.0 MB'
    """
    if bytes_val is None or bytes_val < 0:
        return "0 B"
    val = float(bytes_val)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if val < 1024.0:
            return f"{val:.1f} {unit}" if unit != 'B' else f"{int(val)} B"
        val /= 1024.0
    return f"{val:.1f} PB"


def validate_registration_data(data: dict) -> tuple[bool, str]:
    """
    Validate user registration payload.
    Returns (is_valid, error_message)
    """
    if not data:
        return False, "Request body is empty"

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not name:
        return False, "Full Name is required"
    if len(name) < 2 or len(name) > 100:
        return False, "Full Name must be between 2 and 100 characters"

    if not email:
        return False, "Email address is required"
    if not is_valid_email(email):
        return False, "Please provide a valid email address"

    if not password:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    if password != confirm_password:
        return False, "Passwords do not match"

    return True, ""


def validate_login_data(data: dict) -> tuple[bool, str]:
    """
    Validate user login payload.
    Returns (is_valid, error_message)
    """
    if not data:
        return False, "Request body is empty"

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email:
        return False, "Email address is required"
    if not is_valid_email(email):
        return False, "Please provide a valid email address"

    if not password:
        return False, "Password is required"

    return True, ""

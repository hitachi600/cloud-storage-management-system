"""
Authentication Service Module.
Handles user registration, login verification, and session state.
"""

from flask import session
from database import db
from models.user import User


class AuthService:
    """Authentication and User management operations."""

    @staticmethod
    def register_user(name: str, email: str, password: str) -> tuple[User | None, str]:
        """
        Register a new user in the database.
        Returns (user_instance, error_message).
        """
        clean_email = email.strip().lower()
        clean_name = name.strip()

        # Check if user already exists
        existing_user = User.query.filter_by(email=clean_email).first()
        if existing_user:
            return None, "An account with this email address already exists."

        # Create new user
        new_user = User(
            name=clean_name,
            email=clean_email
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user, ""
        except Exception as e:
            db.session.rollback()
            return None, f"Database error during registration: {str(e)}"

    @staticmethod
    def authenticate_user(email: str, password: str) -> tuple[User | None, str]:
        """
        Authenticate user credentials.
        Returns (user_instance, error_message).
        """
        clean_email = email.strip().lower()
        user = User.query.filter_by(email=clean_email).first()

        if not user:
            return None, "Invalid email or password."

        if not user.check_password(password):
            return None, "Invalid email or password."

        return user, ""

    @staticmethod
    def login_session(user: User):
        """Set user session information."""
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email

    @staticmethod
    def logout_session():
        """Clear user session."""
        session.pop('user_id', None)
        session.pop('user_name', None)
        session.pop('user_email', None)

    @staticmethod
    def get_current_user() -> User | None:
        """Retrieve the currently logged-in user from the database."""
        user_id = session.get('user_id')
        if not user_id:
            return None
        return User.query.get(user_id)

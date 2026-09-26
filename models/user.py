"""
User Model Definition.
Represents registered users of the Cloud Storage system.
"""

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(db.Model):
    """
    User entity for authentication and file ownership.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship: A user can have multiple files. Deleting a user deletes their file records.
    files = db.relationship('FileRecord', backref='owner', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password: str):
        """Hash and set user password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check provided password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize user data to a dictionary (excluding password hash)."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_files': len(self.files)
        }

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}'>"

"""
File Model Definition.
Represents uploaded file metadata and references to physical storage (Local Disk or AWS S3).
"""

from datetime import datetime, timezone
from database import db


class FileRecord(db.Model):
    """
    File metadata record. The physical file is stored in either Local Disk or AWS S3.
    """
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True, index=True)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)  # in bytes
    s3_key = db.Column(db.String(500), nullable=False)
    storage_type = db.Column(db.String(20), default='local', nullable=False)  # 'local' or 's3'
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def formatted_size(self) -> str:
        """Convert byte size into human-readable string (B, KB, MB, GB)."""
        bytes_val = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}" if unit != 'B' else f"{int(bytes_val)} B"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"

    def to_dict(self):
        """Serialize file record to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_type': self.file_type.lower(),
            'file_size': self.file_size,
            'formatted_size': self.formatted_size,
            's3_key': self.s3_key,
            'storage_type': self.storage_type,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None
        }

    def __repr__(self):
        return f"<FileRecord id={self.id} filename='{self.original_filename}' user_id={self.user_id}>"

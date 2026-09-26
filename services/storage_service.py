"""
Storage Service Module for Cloud Storage Management System.
Implements dual-mode storage abstraction:
1. LocalStorageService: Saves files to the local disk (uploads/ folder).
2. S3StorageService: Saves files to an Amazon Web Services (AWS) S3 bucket using boto3.
"""

import os
from pathlib import Path
from abc import ABC, abstractmethod
from flask import current_app, send_file
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class BaseStorageService(ABC):
    """Abstract Base Class for file storage providers."""

    @abstractmethod
    def save_file(self, file_storage, stored_filename: str, user_id: int) -> dict:
        """
        Save the uploaded file to the storage provider.
        Returns metadata dict containing:
            - s3_key / storage_path
            - file_size (in bytes)
            - storage_type ('local' or 's3')
        """
        pass

    @abstractmethod
    def get_file(self, file_record):
        """
        Retrieve file for download or streaming.
        Returns a Flask response (e.g., send_file) or URL redirect.
        """
        pass

    @abstractmethod
    def delete_file(self, file_record) -> bool:
        """
        Delete file from the storage provider.
        Returns True if successful, False otherwise.
        """
        pass


class LocalStorageService(BaseStorageService):
    """
    Local disk storage implementation.
    Stores files inside the configured upload folder, structured by user_id.
    """

    def __init__(self, upload_folder: Path):
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def _get_user_dir(self, user_id: int) -> Path:
        user_dir = self.upload_folder / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def save_file(self, file_storage, stored_filename: str, user_id: int) -> dict:
        user_dir = self._get_user_dir(user_id)
        file_path = user_dir / stored_filename

        # Save to local disk
        file_storage.save(str(file_path))
        file_size = file_path.stat().st_size
        relative_key = f"user_{user_id}/{stored_filename}"

        return {
            's3_key': relative_key,
            'file_size': file_size,
            'storage_type': 'local'
        }

    def get_file(self, file_record):
        user_dir = self._get_user_dir(file_record.user_id)
        file_path = user_dir / file_record.stored_filename

        if not file_path.exists():
            # Fallback to direct key if user directory structure differs
            fallback_path = self.upload_folder / file_record.s3_key
            if fallback_path.exists():
                file_path = fallback_path
            else:
                return None

        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_record.original_filename
        )

    def delete_file(self, file_record) -> bool:
        user_dir = self._get_user_dir(file_record.user_id)
        file_path = user_dir / file_record.stored_filename

        if file_path.exists():
            try:
                os.remove(file_path)
                return True
            except OSError as e:
                print(f"[ERROR] Error removing local file {file_path}: {e}")
                return False
        return True


class S3StorageService(BaseStorageService):
    """
    Amazon Web Services (AWS) S3 Storage implementation using boto3.
    """

    def __init__(self, bucket_name: str, access_key: str, secret_key: str, region: str = 'us-east-1'):
        self.bucket_name = bucket_name
        self.region = region
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    def save_file(self, file_storage, stored_filename: str, user_id: int) -> dict:
        s3_key = f"users/user_{user_id}/{stored_filename}"

        # Read file contents to calculate size and upload to S3
        file_storage.seek(0, os.SEEK_END)
        file_size = file_storage.tell()
        file_storage.seek(0)

        try:
            self.client.upload_fileobj(
                file_storage,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file_storage.content_type or 'application/octet-stream'
                }
            )
            return {
                's3_key': s3_key,
                'file_size': file_size,
                'storage_type': 's3'
            }
        except (NoCredentialsError, ClientError) as e:
            print(f"[ERROR] AWS S3 upload failed: {e}")
            raise RuntimeError(f"AWS S3 upload error: {str(e)}")

    def get_file(self, file_record):
        try:
            # Generate a secure pre-signed download URL valid for 1 hour (3600 seconds)
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_record.s3_key,
                    'ResponseContentDisposition': f'attachment; filename="{file_record.original_filename}"'
                },
                ExpiresIn=3600
            )
            return url
        except ClientError as e:
            print(f"[ERROR] Failed to generate S3 presigned URL: {e}")
            return None

    def delete_file(self, file_record) -> bool:
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=file_record.s3_key
            )
            return True
        except ClientError as e:
            print(f"[ERROR] AWS S3 delete failed for key {file_record.s3_key}: {e}")
            return False


def get_storage_service(app=None) -> BaseStorageService:
    """
    Factory function to return the configured storage service instance.
    Uses 'local' storage or 's3' storage depending on configuration.
    """
    if app is None:
        app = current_app

    storage_type = app.config.get('STORAGE_TYPE', 'local').lower()

    if storage_type == 's3':
        bucket_name = app.config.get('AWS_S3_BUCKET_NAME')
        access_key = app.config.get('AWS_ACCESS_KEY_ID')
        secret_key = app.config.get('AWS_SECRET_ACCESS_KEY')
        region = app.config.get('AWS_REGION', 'us-east-1')

        if not all([bucket_name, access_key, secret_key]):
            print("[WARNING] S3 credentials incomplete. Falling back to LocalStorageService.")
            return LocalStorageService(app.config.get('UPLOAD_FOLDER'))

        return S3StorageService(
            bucket_name=bucket_name,
            access_key=access_key,
            secret_key=secret_key,
            region=region
        )

    # Default to LocalStorageService
    return LocalStorageService(app.config.get('UPLOAD_FOLDER'))

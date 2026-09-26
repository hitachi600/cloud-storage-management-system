"""
Unit tests for storage service abstractions.
"""

import io
from pathlib import Path
from werkzeug.datastructures import FileStorage
from services.storage_service import LocalStorageService
from models.file import FileRecord


def test_local_storage_lifecycle(tmp_path):
    """Test save, get, and delete lifecycle on LocalStorageService."""
    service = LocalStorageService(upload_folder=tmp_path)

    # 1. Save File
    file_content = b"Local storage test bytes."
    stream = io.BytesIO(file_content)
    file_storage = FileStorage(stream=stream, filename="test_doc.txt")

    meta = service.save_file(
        file_storage=file_storage,
        stored_filename="unique_test_doc.txt",
        user_id=1
    )

    assert meta['storage_type'] == 'local'
    assert meta['file_size'] == len(file_content)
    assert "user_1" in meta['s3_key']

    # 2. Check existence on disk
    expected_path = tmp_path / "user_1" / "unique_test_doc.txt"
    assert expected_path.exists()
    assert expected_path.read_bytes() == file_content

    # 3. Delete File
    dummy_record = FileRecord(
        id=1,
        user_id=1,
        original_filename="test_doc.txt",
        stored_filename="unique_test_doc.txt",
        file_type="txt",
        file_size=len(file_content),
        s3_key="user_1/unique_test_doc.txt",
        storage_type="local"
    )

    delete_success = service.delete_file(dummy_record)
    assert delete_success is True
    assert not expected_path.exists()

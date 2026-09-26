"""
Unit & Integration Tests for File Operations and User Isolation.
"""

import io
import json


def login_helper(client, email="student@university.edu", password="SecurePass123!"):
    """Helper to authenticate test client."""
    client.post('/api/login', json={'email': email, 'password': password})


def test_upload_unauthorized(client):
    """Test that unauthenticated file upload is rejected with 401."""
    data = {
        'file': (io.BytesIO(b"Cloud Computing Assignment"), 'assignment.pdf')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 401


def test_upload_valid_file(client, auth_user):
    """Test uploading a valid file."""
    login_helper(client)

    data = {
        'file': (io.BytesIO(b"Hello Cloud Storage! AWS S3 and Local integration works."), 'notes.txt')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    res = json.loads(response.data)
    assert res['success'] is True
    assert res['file']['original_filename'] == 'notes.txt'
    assert res['file']['file_type'] == 'txt'
    assert res['file']['file_size'] > 0


def test_upload_invalid_extension(client, auth_user):
    """Test rejection of unsupported file types."""
    login_helper(client)

    data = {
        'file': (io.BytesIO(b"malicious_script()"), 'virus.exe')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    res = json.loads(response.data)
    assert res['success'] is False
    assert "File type not allowed" in res['error']


def test_list_and_download_file(client, auth_user):
    """Test listing files and downloading uploaded file."""
    login_helper(client)

    content = b"Binary sample pdf content"
    data = {
        'file': (io.BytesIO(content), 'syllabus.pdf')
    }
    upload_res = client.post('/api/upload', data=data, content_type='multipart/form-data')
    file_id = json.loads(upload_res.data)['file']['id']

    # List files
    list_res = client.get('/api/files')
    assert list_res.status_code == 200
    list_data = json.loads(list_res.data)
    assert list_data['count'] == 1

    # Download file
    download_res = client.get(f'/api/download/{file_id}')
    assert download_res.status_code == 200
    assert download_res.data == content


def test_delete_file(client, auth_user):
    """Test deleting an uploaded file."""
    login_helper(client)

    data = {
        'file': (io.BytesIO(b"Temporary file content"), 'temp.txt')
    }
    upload_res = client.post('/api/upload', data=data, content_type='multipart/form-data')
    file_id = json.loads(upload_res.data)['file']['id']

    delete_res = client.delete(f'/api/files/{file_id}')
    assert delete_res.status_code == 200
    assert json.loads(delete_res.data)['success'] is True

    # Check that file list is now empty
    list_res = client.get('/api/files')
    assert json.loads(list_res.data)['count'] == 0

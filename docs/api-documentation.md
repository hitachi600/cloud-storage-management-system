# REST API Documentation

This document describes all REST API endpoints available in the **Cloud Storage Management System**.

---

## 1. Authentication Endpoints

### 1.1 User Registration
- **Endpoint**: `/api/register`
- **Method**: `POST`
- **Description**: Registers a new user account and starts a session.
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "mypassword123",
    "confirm_password": "mypassword123"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "success": true,
    "message": "Account registered successfully!",
    "user": {
      "id": 1,
      "name": "Jane Doe",
      "email": "jane@example.com",
      "created_at": "2026-08-26T15:30:00",
      "total_files": 0
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Missing fields, invalid email format, passwords do not match, or email already registered.

---

### 1.2 User Login
- **Endpoint**: `/api/login`
- **Method**: `POST`
- **Description**: Verifies credentials and creates an authenticated session.
- **Request Body**:
  ```json
  {
    "email": "jane@example.com",
    "password": "mypassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Login successful!",
    "user": {
      "id": 1,
      "name": "Jane Doe",
      "email": "jane@example.com",
      "created_at": "2026-08-26T15:30:00",
      "total_files": 3
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Missing email or password.
  - `401 Unauthorized`: Invalid email or password.

---

### 1.3 User Logout
- **Endpoint**: `/api/logout`
- **Method**: `POST` or `GET`
- **Description**: Clears user session.
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Logged out successfully."
  }
  ```

---

### 1.4 Current User Profile
- **Endpoint**: `/api/me`
- **Method**: `GET`
- **Description**: Returns authenticated user information.
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "user": {
      "id": 1,
      "name": "Jane Doe",
      "email": "jane@example.com",
      "created_at": "2026-08-26T15:30:00",
      "total_files": 5
    }
  }
  ```

---

## 2. File Management Endpoints

### 2.1 Upload File
- **Endpoint**: `/api/upload`
- **Method**: `POST`
- **Authentication**: Required (`@api_login_required`)
- **Request Headers**: `Content-Type: multipart/form-data`
- **Form-Data**:
  - `file`: (Binary File)
- **Response (201 Created)**:
  ```json
  {
    "success": true,
    "message": "File 'project_spec.pdf' uploaded successfully!",
    "file": {
      "id": 12,
      "user_id": 1,
      "original_filename": "project_spec.pdf",
      "stored_filename": "a8f3b201_project_spec.pdf",
      "file_type": "pdf",
      "file_size": 204800,
      "formatted_size": "200.0 KB",
      "s3_key": "users/user_1/a8f3b201_project_spec.pdf",
      "storage_type": "s3",
      "uploaded_at": "2026-08-26 15:35:10"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: No file uploaded or unsupported file extension.
  - `413 Payload Too Large`: File exceeds max content length (16 MB).
  - `500 Internal Server Error`: Storage upload or database failure.

---

### 2.2 List Files
- **Endpoint**: `/api/files`
- **Method**: `GET`
- **Authentication**: Required
- **Query Parameters (Optional)**:
  - `search`: Filter files by partial name (e.g. `?search=report`)
  - `type`: Filter by extension (e.g. `?type=pdf`)
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "count": 2,
    "files": [
      {
        "id": 12,
        "user_id": 1,
        "original_filename": "project_spec.pdf",
        "stored_filename": "a8f3b201_project_spec.pdf",
        "file_type": "pdf",
        "file_size": 204800,
        "formatted_size": "200.0 KB",
        "s3_key": "users/user_1/a8f3b201_project_spec.pdf",
        "storage_type": "s3",
        "uploaded_at": "2026-08-26 15:35:10"
      }
    ]
  }
  ```

---

### 2.3 Get File Details
- **Endpoint**: `/api/files/<file_id>`
- **Method**: `GET`
- **Authentication**: Required
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "file": {
      "id": 12,
      "user_id": 1,
      "original_filename": "project_spec.pdf",
      "stored_filename": "a8f3b201_project_spec.pdf",
      "file_type": "pdf",
      "file_size": 204800,
      "formatted_size": "200.0 KB",
      "s3_key": "users/user_1/a8f3b201_project_spec.pdf",
      "storage_type": "s3",
      "uploaded_at": "2026-08-26 15:35:10"
    }
  }
  ```
- **Error Responses**:
  - `404 Not Found`: File not found or does not belong to logged-in user.

---

### 2.4 Download File
- **Endpoint**: `/api/download/<file_id>`
- **Method**: `GET`
- **Authentication**: Required
- **Behavior**:
  - **Local Storage**: Streams file attachment directly.
  - **AWS S3**: Issues HTTP 302 redirect to a secure, temporary presigned URL.

---

### 2.5 Delete File
- **Endpoint**: `/api/files/<file_id>`
- **Method**: `DELETE`
- **Authentication**: Required
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "message": "File 'project_spec.pdf' deleted successfully."
  }
  ```
- **Error Responses**:
  - `404 Not Found`: File not found or belongs to another user.

---

## 3. Dashboard Endpoints

### 3.1 Get Dashboard Statistics
- **Endpoint**: `/api/dashboard`
- **Method**: `GET`
- **Authentication**: Required
- **Response (200 OK)**:
  ```json
  {
    "success": true,
    "metrics": {
      "total_files": 4,
      "total_storage_bytes": 10485760,
      "formatted_storage": "10.0 MB",
      "storage_quota_bytes": 104857600,
      "formatted_quota": "100.0 MB",
      "storage_percentage": 10.0,
      "storage_mode": "local",
      "type_breakdown": {
        "Documents": 2,
        "Images": 2
      },
      "recent_files": [ ... ]
    }
  }
  ```

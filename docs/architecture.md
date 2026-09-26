# Cloud Storage Management System - System Architecture

## 1. High-Level Architecture Diagram

```
+-------------------------------------------------------------------------+
|                        Client Layer (Browser)                           |
|  - HTML5 Responsive UI                                                  |
|  - CSS3 Glassmorphism & Custom Design System                            |
|  - Vanilla JavaScript (Fetch API, Live XMLHttpRequest Progress)         |
+------------------------------------+------------------------------------+
                                     |  HTTP / REST
                                     v
+------------------------------------+------------------------------------+
|                         Flask Application Layer                         |
|  - App Factory (app.py)                                                 |
|  - Route Handlers (Auth, Files, Dashboard, Pages)                       |
|  - Security & Decorators (@login_required, @api_login_required)         |
|  - Validators (Extension Whitelist, UUID Filename Sanitization)         |
+-------------------+--------------------------------+--------------------+
                    |                                |
                    v                                v
+-------------------+-------------+    +-------------+--------------------+
|         Database Layer          |    |          Storage Layer           |
|  - Flask-SQLAlchemy ORM         |    |  - Storage Service Factory       |
|  - SQLite (Local Dev)           |    |  - LocalStorageService (uploads/)|
|  - AWS RDS (Production)         |    |  - S3StorageService (boto3)      |
+---------------------------------+    +-------------+--------------------+
                                                     |
                                                     v
                                       +-------------+--------------------+
                                       |          Storage Targets         |
                                       |  - Local File System             |
                                       |  - Amazon Web Services S3 Bucket |
                                       +----------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Web & API Layer (`routes/`)
- **`page_routes.py`**: Delivers rendered HTML pages (`index`, `login`, `register`, `dashboard`, `upload`, `files`).
- **`auth_routes.py`**: REST API endpoints for user registration, authentication, session logout, and profile retrieval.
- **`file_routes.py`**: REST API endpoints for uploading, listing, inspecting, streaming/downloading, and deleting files.
- **`dashboard_routes.py`**: Calculates storage consumption, quotas, file type categorization, and recent activity.

### 2.2 Business Logic & Services (`services/`)
- **`BaseStorageService`**: Abstract base class enforcing consistent storage interface methods: `save_file()`, `get_file()`, and `delete_file()`.
- **`LocalStorageService`**: Writes files to partitioned directories (`uploads/user_<id>/<stored_filename>`) and streams them back using Flask's `send_file`.
- **`S3StorageService`**: Connects via AWS Boto3, uploads objects to S3 under `users/user_<id>/<stored_filename>`, generates secure presigned download URLs, and deletes remote S3 objects.
- **`AuthService`**: Encapsulates password hashing with PBKDF2/SHA256, credential validation, and session state.

### 2.3 Data Models & Persistence (`models/`, `database.py`)
- **`User` Entity**: Stores user identification, email index, and encrypted password hash.
- **`FileRecord` Entity**: Stores metadata (original filename, unique UUID filename, MIME/extension, size in bytes, S3 key, storage mode, and upload timestamp).
- **Cascade Relationships**: Ensures when a user account is deleted, all referenced file metadata records are cleanly cleaned up.

---

## 3. Database Schema

```
+----------------------------------+          +--------------------------------------+
|             USERS                |          |                FILES                 |
+----------------------------------+          +--------------------------------------+
| id (PK, Integer)                 | 1      N | id (PK, Integer)                     |
| name (String 100)                |----------| user_id (FK -> users.id, Integer)    |
| email (String 120, Unique, Index)|          | original_filename (String 255)       |
| password_hash (String 256)       |          | stored_filename (String 255, Unique) |
| created_at (DateTime)            |          | file_type (String 50)                |
+----------------------------------+          | file_size (BigInteger, Bytes)        |
                                              | s3_key (String 500)                  |
                                              | storage_type (String 20)             |
                                              | uploaded_at (DateTime)               |
                                              +--------------------------------------+
```

---

## 4. Security Architecture

1. **Password Security**: Passwords are never stored in plaintext. They are hashed using Werkzeug's secure hashing algorithm before writing to database.
2. **Access Isolation**: Every file request verifies that `file.user_id == session['user_id']`. Users cannot read, download, or delete files belonging to other users.
3. **Filename Sanitization**: Uploaded filenames are sanitized with `secure_filename` and prefixed with a cryptographically random UUID4 hex string to prevent file overwrite collisions and directory traversal attacks.
4. **Credential Decoupling**: Sensitive AWS keys and database credentials are strictly passed via environment variables (`.env`).

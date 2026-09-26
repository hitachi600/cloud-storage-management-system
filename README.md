# Cloud Storage Management System ☁️

A beginner-friendly, production-grade Cloud Storage web application built with **Python**, **Flask**, **SQLite** (migratable to **AWS RDS**), and **Amazon Web Services (AWS) S3**.

---

## 📌 Project Overview

The **Cloud Storage Management System** allows registered users to securely upload, browse, inspect, download, and delete their files in the cloud. It features a dual-mode storage engine that lets you run and develop locally without needing an AWS account, while supporting one-click transition to **AWS S3** for real cloud deployment.

---

## ✨ Features

- 👤 **Secure User Authentication**: Registration, PBKDF2 password hashing, and session management.
- ⚡ **Dual Storage Architecture**: Seamlessly toggle between **Local Disk Storage** and **AWS S3 Bucket Storage**.
- 📤 **Interactive Drag-and-Drop Upload**: With real-time upload progress tracking and file validation.
- 📂 **Comprehensive File Management**: Search files by name, filter by extension, inspect metadata, download, and safely delete.
- 📊 **Live Storage Dashboard**: Real-time analytics displaying file count, storage space consumed, quota percentage, and category breakdown.
- 🔒 **Enterprise-Grade Security**: Per-user data isolation, collision-free UUID filename sanitization, and extension whitelisting.

---

## 🛠️ Technologies Used

- **Backend**: Python 3.10+, Flask 3.0, Flask-SQLAlchemy, Werkzeug, python-dotenv
- **Cloud Storage**: Amazon Web Services (AWS) S3, Boto3 SDK
- **Database**: SQLite (Local Development) / AWS RDS (Production ready)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), Vanilla JavaScript (ES6+)
- **Testing**: Pytest, Pytest-Flask

---

## 🏗️ Cloud System Architecture

```
User (Browser)
      ↓
Frontend (HTML5 / CSS3 / Vanilla JS)
      ↓  (HTTP REST API)
Flask Backend Application (app.py, routes, services)
      ↓
┌───────────────────────────────────────────────┐
│ Database (SQLite / AWS RDS)                   │
│ Stores User Accounts & File Metadata          │
└───────────────────────────────────────────────┘
      ↓
┌───────────────────────────────────────────────┐
│ Storage Service Abstraction Layer             │
│ ├─ Local Storage Engine (uploads/ folder)     │
│ └─ AWS S3 Storage Engine (Amazon S3 Bucket)   │
└───────────────────────────────────────────────┘
```

---

## 🚀 Quick Start & Installation

### Step 1: Navigate to the Project Directory
```bash
cd C:\Users\Gauth\.gemini\antigravity-ide\scratch\cloud-storage-management-system
```

### Step 2: (Optional) Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` (a working `.env` is already configured for local mode):
```bash
copy .env.example .env
```

### Step 5: Run the Application
```bash
python app.py
```

Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## ⚙️ Environment Variables Explained

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `FLASK_APP` | Application entry point file | `app.py` |
| `FLASK_ENV` | Environment mode (`development` / `production`) | `development` |
| `SECRET_KEY` | Secret key used for session cryptographic signing | `cloud-storage-secret-key-2026` |
| `STORAGE_TYPE` | Storage engine to use: `local` or `s3` | `local` |
| `UPLOAD_FOLDER` | Directory for local file storage when `STORAGE_TYPE=local` | `uploads` |
| `DATABASE_URI` | Database connection string (SQLite or AWS RDS PostgreSQL/MySQL) | `sqlite:///instance/cloud_storage.db` |
| `MAX_CONTENT_LENGTH` | Maximum upload file size in bytes (16 MB) | `16777216` |
| `ALLOWED_EXTENSIONS` | Comma-separated list of allowed file extensions | `pdf,jpg,jpeg,png,txt,docx,csv,xlsx,zip` |
| `AWS_ACCESS_KEY_ID` | IAM User Access Key for Amazon S3 | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY`| IAM User Secret Key for Amazon S3 | `wJalrXUtnFEMI...` |
| `AWS_REGION` | AWS Region where the S3 bucket is hosted | `us-east-1` |
| `AWS_S3_BUCKET_NAME` | Name of your Amazon S3 bucket | `my-cloud-storage-bucket` |

---

## 💾 Storage Modes

### 1. Local Storage Mode (Default - Zero AWS Cost)
By default, `STORAGE_TYPE=local` is set in `.env`.
Files are stored securely in the `uploads/user_<id>/` folder on your local disk, and the database keeps track of the file metadata in `instance/cloud_storage.db`. This mode requires no internet connection or AWS credentials.

### 2. AWS S3 Cloud Storage Mode
To switch to real Amazon S3 storage:
1. Create an S3 Bucket and IAM User with S3 permissions (see [docs/aws-setup.md](docs/aws-setup.md)).
2. Update your `.env` file:
   ```env
   STORAGE_TYPE=s3
   AWS_ACCESS_KEY_ID=your_aws_access_key_id
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
   AWS_REGION=us-east-1
   AWS_S3_BUCKET_NAME=your_s3_bucket_name
   ```
3. Restart the server: `python app.py`.

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:
```bash
pytest -v
```

All 12 automated unit and integration tests will execute, verifying user registration, login security, file upload validation, downloads, and storage operations.

---

## 📚 Detailed Documentation

Detailed guides are located inside the `docs/` folder:
- 📖 [Project Overview](docs/project-overview.md): Scope, features, and technology stack.
- 🏛️ [System Architecture](docs/architecture.md): High-level architecture and database schema.
- ☁️ [AWS Setup Guide](docs/aws-setup.md): Step-by-step tutorial to create an S3 bucket and IAM user.
- 🔌 [REST API Documentation](docs/api-documentation.md): Comprehensive endpoint specifications with JSON payloads.

---

## 🔮 Future Enhancements

- 🔗 **File Sharing**: Generate public or password-protected shareable download links with expiration timers.
- 🚀 **AWS CloudFront CDN**: Distribute file downloads globally with edge caching.
- 🗄️ **AWS RDS Migration**: Deploy PostgreSQL / MySQL on AWS RDS with connection pooling.
- 🐳 **Docker & ECS Deployment**: Containerize the Flask backend and deploy using AWS ECS or AWS Elastic Beanstalk.
- 👥 **Role-Based Access Control (RBAC)**: Administrator and standard user permission tiers.
- 🔄 **File Versioning**: Maintain revision history for modified documents.

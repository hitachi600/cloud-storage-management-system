# Cloud Storage Management System - Project Overview

## 1. Executive Summary

The **Cloud Storage Management System** is a full-stack, cloud-native web application developed to demonstrate core principles of modern cloud computing, distributed file storage, relational metadata management, and secure web application development.

It allows registered users to securely upload, inspect, manage, download, and delete files across a dual-storage infrastructure:
1. **Local Storage Engine**: Designed for zero-cost, immediate local development and offline demonstrations.
2. **Amazon Web Services (AWS) S3 Storage Engine**: Designed for highly available, scalable, cloud-native object storage in production.

---

## 2. Project Objectives

- **Cloud Storage Abstraction**: Understand how modern cloud applications abstract the underlying storage layer from the business logic.
- **Relational Metadata Mapping**: Decouple binary file blobs from database records by storing physical objects in S3/disk while keeping indexed metadata in SQLite / AWS RDS.
- **Data Security & Privacy**: Implement secure password hashing, session-based access control, file type whitelisting, and strict per-user authorization boundaries.
- **Interactive User Experience**: Provide a modern, responsive web dashboard with live upload progress tracking, file analytics, and instant feedback.

---

## 3. Core Features

| Feature | Description |
| :--- | :--- |
| **User Authentication** | User registration with input validation, PBKDF2 password hashing, and session management. |
| **Dual Storage Mode** | Switch between local disk storage and AWS S3 simply by modifying environment variables. |
| **Drag-and-Drop Upload** | Intuitive file upload zone with live upload progress bar and file validation. |
| **File Management** | File listing with real-time search, extension filtering, detailed metadata view, and downloads. |
| **Safe Deletion** | Deletes both the database metadata record and the physical storage object on AWS S3 / disk. |
| **Analytics Dashboard** | Live computation of total files, storage space consumed, quota usage %, and file type breakdown. |
| **Error Handling** | Graceful error responses for file size limits (16 MB), unauthorized access, and network failures. |

---

## 4. Technology Stack Summary

- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), Vanilla JavaScript (ES6+), FontAwesome Icons.
- **Backend**: Python 3.10+, Flask 3.0, Flask-SQLAlchemy, Werkzeug, python-dotenv.
- **Cloud & SDK**: AWS S3, Boto3 SDK, Botocore.
- **Database**: SQLite 3 (Development) / AWS RDS PostgreSQL or MySQL (Production).
- **Testing**: Pytest, Pytest-Flask.

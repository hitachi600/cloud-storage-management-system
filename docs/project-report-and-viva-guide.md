# Academic Project Report & Viva / Presentation Preparation Guide

This guide is designed to help college students explain, demonstrate, and defend the **Cloud Storage Management System** during project evaluations, seminars, and viva examinations.

---

## 1. Project Summary (For Report Abstract)

> **Abstract**:  
> In modern distributed computing, monolithic file storage architectures create severe bottlenecks in scalability, availability, and security. This project presents the **Cloud Storage Management System**, a decoupled, cloud-native web application built using Python (Flask), SQLite (migratable to AWS RDS), and Amazon Web Services (AWS) Simple Storage Service (S3). The system implements a dual-mode storage engine allowing seamless local development and production cloud deployment. Binary file assets are stored in object storage, while relational metadata is indexed separately, ensuring sub-second queries, per-user data isolation, and cryptographic security.

---

## 2. Key Cloud Computing Concepts Demonstrated

### 1. Object Storage vs. Block/File Storage
- **Block Storage (e.g., AWS EBS)**: Raw drive volumes mounted to a specific OS instance.
- **Object Storage (e.g., AWS S3)**: Highly scalable flat data storage where each file is an "object" with data, a unique key, and customizable metadata. Accessible via HTTP/REST APIs.
- **In our project**: We use Amazon S3 as the object store, allowing virtually infinite scalability without managing physical hard drives.

### 2. Decoupled Metadata & Binary Separation
- **Why NOT store files in the SQL Database as BLOBs?**
  - Storing binary files in SQL databases bloats database backups, exhausts memory buffers, degrades index performance, and incurs high compute costs.
  - **Our Architecture**: Database stores only small metadata records (filename, file size, MIME type, S3 key, owner ID, timestamp), while the binary data lives in AWS S3 or the `uploads/` folder.

### 3. Presigned URLs for Secure Cloud Downloads
- Instead of streaming large files through our Flask web server (which consumes server bandwidth and CPU), S3 can generate **Time-Limited Presigned URLs** (e.g., valid for 60 minutes) signed with AWS cryptographic credentials. The client downloads directly from Amazon S3's high-speed CDN backbone.

### 4. Cloud Security & IAM Least-Privilege
- Never use AWS Root accounts.
- We configure a dedicated IAM user (`cloud-storage-app-user`) with restricted policies.
- Secrets and keys are strictly injected via `.env` environment variables and excluded from version control via `.gitignore`.

---

## 3. Step-by-Step 5-Minute Live Presentation Script

| Step | Action | What to Explain to Evaluators |
| :--- | :--- | :--- |
| **1. Introduction (30s)** | Open `http://127.0.0.1:5000` | "This is our Cloud Storage Management System. The navbar displays our active storage mode (LOCAL or AWS S3). Today we demonstrate both local resilience and cloud integration." |
| **2. Login / Register (45s)** | Login with `demo@example.com` / `Password123!` | "Passwords are cryptographically hashed using PBKDF2 with SHA-256 before storage. Sessions are isolated per user." |
| **3. Dashboard Analytics (60s)** | Show Dashboard Metrics | "Our dashboard calculates real-time storage metrics: Total file count, consumed storage bytes, quota percentage, and automatic category categorization (Documents, Images, Archives)." |
| **4. Live File Upload (60s)** | Go to `/upload` & drag-drop a file | "We built a drag-and-drop zone with client-side extension validation and an `XMLHttpRequest` live upload progress bar. In the backend, filenames are sanitized with UUIDs to prevent collisions." |
| **5. File Explorer & Download (45s)** | Go to `/files`, search, view details, download | "Users can search in real-time, filter by extension, inspect full metadata (S3 Key, exact byte count), and download or delete files safely." |
| **6. Architecture & AWS Switch (60s)** | Show `.env` & `storage_service.py` | "Our backend uses the Factory Design Pattern. Switching from Local mode to AWS S3 mode requires changing just one line in `.env` without modifying a single line of backend logic." |

---

## 4. Top 15 Viva Questions & Ideal Answers

### Q1: Why did you separate file storage from the database?
**Answer**: Databases are optimized for structured queries and transactional consistency (ACID). Storing binary files (BLOBs) inside tables causes database bloat, degrades RAM caching, slows down queries, and makes database backups massive. By storing files in Object Storage (S3/disk) and keeping only metadata in the DB, the system achieves maximum performance and scalability.

### Q2: How does the dual-mode storage engine work in your code?
**Answer**: We implemented the **Factory Pattern** with an abstract base class `BaseStorageService` defining `save_file()`, `get_file()`, and `delete_file()`. Two concrete classes (`LocalStorageService` and `S3StorageService`) implement these methods. The application reads `STORAGE_TYPE` from environment variables and dynamically instantiates the appropriate service.

### Q3: How do you prevent two users from overwriting files with the same name?
**Answer**: When a file is uploaded, our validator generates a collision-free stored filename using `uuid.uuid4().hex` prefixed to the sanitized filename (e.g. `9f8e7d6c_report.pdf`). The original name is retained in the database for display and download.

### Q4: How are passwords protected?
**Answer**: We use **Werkzeug's PBKDF2 (Password-Based Key Derivation Function 2)** with SHA-256 hashing and unique salts. Plaintext passwords are never stored in the database or logs.

### Q5: How would you migrate this application from SQLite to AWS RDS?
**Answer**: Because we use SQLAlchemy ORM, we only need to change the `DATABASE_URI` environment variable in `.env` from `sqlite:///instance/...` to `postgresql://user:password@rds-endpoint:5432/cloud_storage_db`. No code changes are required.

### Q6: What is a Presigned S3 URL and why is it useful?
**Answer**: A presigned URL is a temporary URL generated by the AWS SDK containing cryptographic authentication query parameters. It allows a client to download or upload directly to an Amazon S3 bucket without making the bucket public or routing high-bandwidth binary data through our web server.

### Q7: What are the security protections implemented against unauthorized file access?
**Answer**: 
1. `@login_required` and `@api_login_required` decorators check active session tokens.
2. Every file operation explicitly checks `FileRecord.user_id == session['user_id']`. A user cannot view, download, or delete another user's files even if they guess the file ID.

### Q8: What happens when a user deletes a file?
**Answer**: The application executes a two-step deletion: first, it instructs the active storage engine (S3 or local disk) to delete the physical binary file. Second, it deletes the database metadata record from SQLite/RDS.

### Q9: How is file size and file type validation enforced?
**Answer**: 
1. Extension whitelisting on both client (HTML input accept and JS) and backend (`ALLOWED_EXTENSIONS`).
2. Maximum file size is enforced via Flask's `MAX_CONTENT_LENGTH` (16 MB) returning HTTP 413 if exceeded.

### Q10: What are the storage tiers in AWS S3 and how could they be used here?
**Answer**:
- **S3 Standard**: For frequently accessed files (default).
- **S3 Standard-Infrequent Access (S3-IA)**: For files accessed less often at lower storage cost.
- **S3 Glacier / Glacier Deep Archive**: For long-term archiving of cold data at extremely low cost. Lifecycle rules in AWS S3 can transition older user files automatically.

### Q11: What is the purpose of `.env.example`?
**Answer**: To document the required configuration keys and structure for developers without committing actual secret API keys or passwords to version control repositories.

### Q12: How does the application maintain responsive UI without blocking during uploads?
**Answer**: The frontend uses asynchronous JavaScript (`XMLHttpRequest` and `FormData`) to stream the file in the background while updating a live progress bar based on `e.loaded` and `e.total` bytes.

### Q13: What is the role of Boto3 in this project?
**Answer**: **Boto3** is the official AWS SDK for Python. It provides the Python API to create clients for AWS services, allowing us to upload objects, generate presigned URLs, and delete objects in Amazon S3.

### Q14: How does containerization with Docker benefit this cloud project?
**Answer**: Docker packages the application code, Python runtime, system libraries, and dependencies into an immutable image. This ensures identical execution across development, testing, and production cloud environments (such as AWS ECS or Elastic Beanstalk).

### Q15: What are the future cloud enhancements planned for this system?
**Answer**: Integrating AWS CloudFront (CDN) for global edge caching, AWS Cognito for OAuth2 / social logins, and AWS Lambda with S3 Event triggers for automated image thumbnail generation and malware scanning.

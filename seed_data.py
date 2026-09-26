"""
Database & File Seeder Script.
Populates the Cloud Storage system with a demo student account and realistic sample files
for instant demonstration and presentation.
"""

import io
from pathlib import Path
from app import create_app
from database import db
from models.user import User
from models.file import FileRecord
from utils.validators import sanitize_filename, get_file_extension


SAMPLE_FILES = [
    {
        'filename': 'Cloud_Computing_Seminar_Report.pdf',
        'content': b"%PDF-1.4 Sample PDF content for Cloud Computing Academic Project Demonstration.\nCloud Storage architectures allow scalable and elastic file distribution.",
        'type': 'pdf'
    },
    {
        'filename': 'AWS_S3_Architecture_Diagram.png',
        'content': b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x01\x00\x08\x06\x00\x00\x00Sample PNG binary data for cloud architecture visual representation.",
        'type': 'png'
    },
    {
        'filename': 'Project_Specification_v2.docx',
        'content': b"PK\x03\x04 Sample Microsoft Word Document Specification containing functional and non-functional requirements.",
        'type': 'docx'
    },
    {
        'filename': 'Quarterly_Storage_Usage.xlsx',
        'content': b"PK\x03\x04 Sample Excel Spreadsheet detailing storage consumption metrics per department.",
        'type': 'xlsx'
    },
    {
        'filename': 'Distributed_Systems_Lecture_Notes.txt',
        'content': b"Distributed Systems Lecture Notes\n- CAP Theorem: Consistency, Availability, Partition Tolerance\n- Object Storage vs Block Storage vs File Storage\n- Amazon S3 bucket policies and IAM least-privilege security.",
        'type': 'txt'
    },
    {
        'filename': 'Dataset_Archive_2026.zip',
        'content': b"PK\x03\x04\x14\x00\x00\x00\x08\x00 Sample ZIP archive containing training datasets and metadata logs.",
        'type': 'zip'
    }
]


def seed_database():
    app = create_app()
    with app.app_context():
        print("----------------------------------------------------------------")
        print("[*] Seeding Cloud Storage Database with Demo Account & Files...")
        print("----------------------------------------------------------------")

        # Create or update demo user
        demo_email = "demo@example.com"
        user = User.query.filter_by(email=demo_email).first()

        if not user:
            user = User(
                name="Alex Mercer (Student Demo)",
                email=demo_email
            )
            user.set_password("Password123!")
            db.session.add(user)
            db.session.commit()
            print(f"[OK] Created Demo User: {demo_email} | Password: Password123!")
        else:
            print(f"[*] Demo user {demo_email} already exists (ID: {user.id})")

        # Setup local user uploads directory
        uploads_dir = Path(app.config['UPLOAD_FOLDER']) / f"user_{user.id}"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Populate sample files
        added_count = 0
        for item in SAMPLE_FILES:
            clean_name, stored_name = sanitize_filename(item['filename'])
            file_path = uploads_dir / stored_name

            # Write sample file to local disk
            file_path.write_bytes(item['content'])
            file_size = len(item['content'])

            # Check if record already exists
            existing_record = FileRecord.query.filter_by(user_id=user.id, original_filename=item['filename']).first()
            if not existing_record:
                file_record = FileRecord(
                    user_id=user.id,
                    original_filename=item['filename'],
                    stored_filename=stored_name,
                    file_type=item['type'],
                    file_size=file_size,
                    s3_key=f"user_{user.id}/{stored_name}",
                    storage_type="local"
                )
                db.session.add(file_record)
                added_count += 1

        db.session.commit()
        print(f"[OK] Successfully seeded {added_count} demo files!")
        print("----------------------------------------------------------------")
        print("Demo Credentials:")
        print("  Email:    demo@example.com")
        print("  Password: Password123!")
        print("  URL:      http://127.0.0.1:5000/login")
        print("----------------------------------------------------------------")


if __name__ == '__main__':
    seed_database()

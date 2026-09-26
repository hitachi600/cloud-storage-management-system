# AWS S3 Setup & Configuration Guide

This guide walks you through setting up an **Amazon Web Services (AWS)** account, creating an **S3 Bucket**, creating an **IAM User** with least-privilege permissions, and configuring your application `.env` file to use AWS S3.

---

## Step 1: Create an AWS S3 Bucket

1. Sign in to the [AWS Management Console](https://aws.amazon.com/console/).
2. In the top search bar, search for **S3** and select **S3 (Scalable Storage in the Cloud)**.
3. Click the orange **Create bucket** button.
4. Configure your bucket settings:
   - **Bucket name**: Enter a unique name (e.g., `cloud-storage-vault-student-2026`).
   - **AWS Region**: Choose a region close to you (e.g., `us-east-1` or `ap-south-1`).
   - **Block Public Access settings for this bucket**: Keep **Block *all* public access** checked (Recommended for maximum security, since our backend will handle secure access via presigned URLs and SDK).
   - **Bucket Versioning**: Optional (keep disabled or enable if versioning is desired).
   - **Default Encryption**: Server-side encryption with Amazon S3 managed keys (SSE-S3).
5. Click **Create bucket** at the bottom of the page.

---

## Step 2: Create an IAM User with S3 Permissions

For security best practices, never use your AWS root account credentials. Create a dedicated IAM user:

1. In the AWS Console, search for **IAM** (Identity and Access Management).
2. In the left navigation menu, click **Users**, then click **Create user**.
3. **User details**: Enter a name such as `cloud-storage-app-user`. Click **Next**.
4. **Set permissions**:
   - Choose **Attach policies directly**.
   - Search for `AmazonS3FullAccess` (or create a custom policy restricting to your specific bucket).
   - Select the checkbox next to the policy. Click **Next**.
5. Click **Create user**.

---

## Step 3: Generate Access Keys for IAM User

1. In the **Users** list, click on your newly created user (`cloud-storage-app-user`).
2. Click on the **Security credentials** tab.
3. Scroll down to the **Access keys** section and click **Create access key**.
4. Select **Application running outside AWS** and click **Next**.
5. (Optional) Enter a description tag like `Cloud Storage Project`.
6. Click **Create access key**.
7. **Important**: Copy your **Access key ID** and **Secret access key** immediately or download the `.csv` file. You will not be able to view the secret key again.

---

## Step 4: Configure Environment Variables

Open the `.env` file in the root of your project and update the following settings:

```env
# Switch storage mode from 'local' to 's3'
STORAGE_TYPE=s3

# AWS S3 Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=cloud-storage-vault-student-2026
```

---

## Step 5: Verify S3 Integration

1. Start your application:
   ```bash
   python app.py
   ```
2. Look at the startup terminal output to verify:
   ```
   ================================================================
    Cloud Storage Management System running at: http://127.0.0.1:5000
    Storage Mode: S3
   ================================================================
   ```
3. Log in to the application and upload a file.
4. Go to your AWS S3 Console, open your bucket, and you will see the file stored under `users/user_<id>/<stored_filename>`.

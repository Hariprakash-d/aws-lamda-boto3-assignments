# Automated S3 Bucket Cleanup (AWS Lambda & Boto3)

An automated AWS Lambda solution written in Python 3.12+ using the Boto3 SDK to clean up stale objects from a specific Amazon S3 bucket. This function safely processes large buckets using S3 paginators, evaluates timezone-aware timestamps, and purges files older than 30 days.

## 🚀 Architectural Overview

*   **Amazon S3**: Hosts the target storage bucket containing volatile or temporary objects.
*   **AWS Lambda**: Executes a serverless Python script that programmatically scans and deletes stale data.
*   **IAM Role**: Enforces least-privilege security by scoping access exclusively to `s3:ListBucket` and `s3:DeleteObject` for the designated bucket.

---

## 🛠️ Setup & Deployment Steps

### 1. Configure the Target S3 Bucket
1. Log into the AWS Management Console and open the **Amazon S3** service dashboard.
2. Create a new bucket with a globally unique name (e.g., `my-cleanup-assignment-bucket-123`).
3. Retain default security and encryption settings.
4. Upload test files into the bucket to act as sample objects.

### 2. Establish the IAM Execution Role
1. Navigate to the **IAM** (Identity and Access Management) console.
2. Create a new execution role selecting **Lambda** as the trusted entity.
3. Attach the following **Inline Policy** to ensure strict adherence to the principle of least privilege (replace `YOUR-BUCKET-NAME` with your actual bucket identifier):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3CleanupPermissions",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR-BUCKET-NAME",
                "arn:aws:s3:::YOUR-BUCKET-NAME/*"
            ]
        }
    ]
}
```

### 3. Deploy the AWS Lambda Function
1. Navigate to the **AWS Lambda** console and select **Create function** from scratch.
2. Select **Python 3.12** (or higher) as your active runtime environment.
3. Assign the existing execution role constructed in the previous step.
4. Replace the base template code with the production implementation provided in `lambda_function.py`.
5. Update the global configuration variable `BUCKET_NAME` to point to your target bucket.
6. Click **Deploy** to compile and stage your code changes.

---

## 🧪 Testing and Validation

1. **Testing Setup (Short-Term Window)**: Modify the age evaluation variable inside the script code from `days=AGE_THRESHOLD_DAYS` to `minutes=5` to easily capture mock data.
2. **Execution**: Execute the workflow manually by triggering a blank test event.
3. **Log Verification**: Confirm via the execution console output or Amazon CloudWatch logs that items matching the timeframe are deleted while newer files are explicitly kept.
4. **Production Readiness**: Revert the threshold evaluation parameter to `days=30` and re-deploy your functions.

---

## 📘 Production Architecture Discussion

### Why use AWS Lambda instead of Native S3 Lifecycle Rules?
S3 Lifecycle Rules process data-purging actions natively with zero overhead and zero operational code. However, utilizing an AWS Lambda execution architecture becomes necessary when your workflows require:
*   **Advanced Evaluation Logic**: Inspecting object naming patterns, dynamic file metadata, or parsing inner contents before executing deletions.
*   **Cross-Service Dependencies**: Querying external configurations or state tables (e.g., Amazon DynamoDB) to check if a file is ready for removal.
*   **Operational Logging & Events**: Injecting transactional telemetry such as broadcasting a Slack alert, updating metrics, or publishing event logs before purging an object.

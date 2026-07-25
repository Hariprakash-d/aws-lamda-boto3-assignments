# Automated EBS Snapshot Creation and Cleanup Engine

An event-driven AWS serverless architecture that automates Elastic Block Store (EBS) volume backups and enforces a strict 30-day retention cleanup policy. This project uses an AWS Lambda function running Python (Boto3) orchestrated by Amazon EventBridge cron schedules.

## Architecture Blueprint

---

## 🛠️ Step-by-Step Implementation Guide

### Step 1: Identify Target EBS Volume
1. Navigate to the **Amazon EC2 Console**.
2. Click **Volumes** under the *Elastic Block Store* menu.
3. Select an existing volume or create a new 1 GiB GP3 test volume.
4. Copy your **Volume ID** (e.g., `vol-0123456789abcdef0`).

### Step 2: Configure Least-Privilege IAM Execution Role
1. Navigate to the **IAM Console** and click **Roles** > **Create role**.
2. Select **AWS service** as the trusted entity and **Lambda** as the use case.
3. Advance to the final step, name the role `LambdaEBSSnapshotExecutionRole`, and click **Create**.
4. Open your new role, click **Add permissions** > **Create inline policy**, and select the **JSON** editor.
5. Paste the following production-grade configuration block:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EC2SnapshotManagement",
            "Effect": "Allow",
            "Action": [
                "ec2:CreateSnapshot",
                "ec2:DescribeSnapshots",
                "ec2:DeleteSnapshot",
                "ec2:CreateTags"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudWatchLogging",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```
6. Click **Next**, name the inline policy `EBSBackupManagerInlinePolicy`, and click **Create policy**.

### Step 3: Deploy the Lambda Function
1. Navigate to the **AWS Lambda Console** and click **Create function**.
2. Select **Author from scratch** and use these parameters:
   * **Function name**: `AutomatedEBSBackupEngine`
   * **Runtime**: `Python 3.12` (or latest available Python 3.x)
   * **Execution role**: Choose *Use an existing role* and select `LambdaEBSSnapshotExecutionRole`.
3. In the **Code source** editor, replace the boilerplate code inside `lambda_function.py` with the script provided in the [Source Code](#source-code) section below.
4. **Important**: Modify line 7 of the script, replacing `"YOUR_VOLUME_ID_HERE"` with your actual EBS Volume ID.
5. Click **Deploy**.
6. Navigate to **Configuration** > **General configuration** > **Edit**. Change the **Timeout** to **1 minute** and click **Save**.

### Step 4: Establish the EventBridge Automation Schedule
1. Open the **Amazon EventBridge Console** and select **Rules** > **Create rule**.
2. Name the rule `WeeklyEBSBackupSchedule` and select **Schedule** as the *Rule type*.
3. Click **Continue to create rule**.
4. Select **Cron expression** and input `0 0 ? * SUN *` to trigger the job weekly every Sunday at 00:00 UTC.
5. Set the Target type to **AWS service** and select **Lambda function**.
6. Choose `AutomatedEBSBackupEngine` from the function dropdown menu.
7. Click through the remaining default configuration screens and choose **Create rule**.

### Step 5: Manual Execution and System Testing
1. Return to the **Lambda Console** for your function.
2. Select the **Test** tab, create a dummy test event with any basic name, and click **Save**.
3. Click **Test** to manually run the engine.
4. Verify the **Execution results**:
   * Inspect the log streams to confirm the newly initialized snapshot ID is printed.
   * *Note*: Old snapshot deletions will show as 0 items on the initial run until historical snapshots exceed the 30-day age marker.
5. Open the **EC2 Console** under **Snapshots** to confirm the fresh item exists with the tag `CreatedBy=Lambda-Backup`.

---

## 💻 Source Code

```python
import boto3
import datetime
from botocore.exceptions import ClientError

# System Configurations
VOLUME_ID = "YOUR_VOLUME_ID_HERE"  # <-- Swap with your valid target volume ID
RETENTION_DAYS = 30
TAG_KEY = "CreatedBy"
TAG_VALUE = "Lambda-Backup"

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    now = datetime.datetime.now(datetime.timezone.utc)
    
    print(f"Starting EBS snapshot operations for volume: {VOLUME_ID}")
    
    # Phase 1: Automated Snapshot Generation & Isolation Tagging
    try:
        snapshot = ec2.create_snapshot(
            VolumeId=VOLUME_ID,
            Description=f"Automated backup of {VOLUME_ID}",
            TagSpecifications=[{
                'ResourceType': 'snapshot',
                'Tags': [{'Key': TAG_KEY, 'Value': TAG_VALUE}]
            }]
        )
        new_snapshot_id = snapshot['SnapshotId']
        print(f"SUCCESSFULLY CREATED SNAPSHOT ID: {new_snapshot_id}")
    except ClientError as e:
        print(f"CRITICAL: Failed to create snapshot: {e}")
        return

    # Phase 2: Targeted Query and Retention Expiration Purge
    try:
        response = ec2.describe_snapshots(
            OwnerIds=['self'],
            Filters=[{'Name': f'tag:{TAG_KEY}', 'Values': [TAG_VALUE]}]
        )
        
        for snap in response['Snapshots']:
            snap_id = snap['SnapshotId']
            
            # Prevent self-deletion of the newly deployed asset in this loop
            if snap_id == new_snapshot_id:
                continue
                
            snap_start_time = snap['StartTime']
            age = now - snap_start_time
            
            if age.days > RETENTION_DAYS:
                print(f"EXPIRATION DETECTED: Snapshot ID {snap_id} is {age.days} days old.")
                ec2.delete_snapshot(SnapshotId=snap_id)
                print(f"SUCCESSFULLY DELETED SNAPSHOT ID: {snap_id}")
                
    except ClientError as e:
        print(f"ERROR: Fault encountered while enforcing retention logic: {e}")
```

---

## 🧠 Architectural Trade-offs: Lambda vs. AWS DLM

While **AWS Data Lifecycle Manager (DLM)** serves as native, configuration-driven policy management for standard operational backups, **AWS Lambda** is the preferred enterprise design choice for these scenarios:

*   **Custom Retention Schemes**: DLM structures are bound to fixed daily, weekly, or monthly intervals. Lambda allows programmatic logic to compute complex custom schedules, such as variable retention based on fiscal quarters or dynamic data-tiering rules.
*   **Cross-Account Isolation**: Lambda provides the programmatic freedom to modify cross-account resource sharing parameters on the fly, immediately duplicating or migrating snapshot elements into isolated security and backup target accounts.
*   **Advanced Multi-Channel Alerting**: Lambda integrates natively into complex pipelines to parse execution metadata, dispatch formatting blocks to external third-party logging engines, or trigger interactive rich-text warnings directly to Slack/Teams webhooks.
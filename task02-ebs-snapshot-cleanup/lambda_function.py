import boto3
import datetime
from botocore.exceptions import ClientError

# Configuration variables
VOLUME_ID = "YOUR_VOLUME_ID_HERE"  # <-- Paste your volume ID from Step 1
RETENTION_DAYS = 30
TAG_KEY = "CreatedBy"
TAG_VALUE = "Lambda-Backup"

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    now = datetime.datetime.now(datetime.timezone.utc)
    
    print(f"Starting EBS snapshot operations for volume: {VOLUME_ID}")
    
    # 1. Create a snapshot and tag it
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
        print(f"CREATED SNAPSHOT ID: {new_snapshot_id}")
    except ClientError as e:
        print(f"Error creating snapshot: {e}")
        return

    # 2. List snapshots with target tag and delete older than 30 days
    try:
        response = ec2.describe_snapshots(
            OwnerIds=['self'],
            Filters=[{'Name': f'tag:{TAG_KEY}', 'Values': [TAG_VALUE]}]
        )
        
        for snap in response['Snapshots']:
            snap_id = snap['SnapshotId']
            
            # Skip checking the snapshot we just created in this execution
            if snap_id == new_snapshot_id:
                continue
                
            snap_start_time = snap['StartTime']
            age = now - snap_start_time
            
            if age.days > RETENTION_DAYS:
                print(f"DELETING EXPIRED SNAPSHOT ID: {snap_id} (Age: {age.days} days)")
                ec2.delete_snapshot(SnapshotId=snap_id)
                
    except ClientError as e:
        print(f"Error evaluating or deleting snapshots: {e}")

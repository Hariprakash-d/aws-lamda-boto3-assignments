import boto3
from datetime import datetime, timezone, timedelta

# Configuration
BUCKET_NAME = "my-cleanup-assignment-bucket-123"  # Change to your bucket name
AGE_THRESHOLD_MINUTES = 5 

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    current_time = datetime.now(timezone.utc)
    deleted_count = 0
    
    # Initialize the S3 paginator to handle large buckets safely
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=BUCKET_NAME)
    
    print(f"Starting cleanup scan for bucket: {BUCKET_NAME}")
    
    for page in pages:
        # Check if bucket contains objects
        if 'Contents' not in page:
            print("No objects found in the bucket.")
            return {"statusCode": 200, "body": "Bucket is empty."}
            
        for obj in page['Contents']:
            object_key = obj['Key']
            object_time = obj['LastModified'] # This is timezone-aware (UTC)
            
            # Calculate object age
            object_age = current_time - object_time
            
            # Check if object is older than the minute threshold
            if object_age > timedelta(minutes=AGE_THRESHOLD_MINUTES):
                print(f"Deleting older object: {object_key} (Age: {object_age})")
                
                # Perform the deletion
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=object_key)
                deleted_count += 1
            else:
                print(f"Keeping newer object: {object_key} (Age: {object_age})")
                
    return {
        "statusCode": 200,
        "body": f"Cleanup complete. Total objects deleted: {deleted_count}"
    }

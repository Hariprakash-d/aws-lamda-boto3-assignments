import boto3
import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # 1. Parse instance identity and runtime operational metrics from the payload
    instance_id = event.get('detail', {}).get('instance-id')
    state = event.get('detail', {}).get('state')
    
    if not instance_id:
        print("ERROR: Event payload is missing a valid instance-id attribute.")
        return
        
    print(f"Intercepted state-change notification. Instance: {instance_id} is in '{state}' state.")
    
    # Generate timestamp metrics matching target environment requirements
    current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    
    # 2. Construct tag arrays mapping out corporate ownership definitions
    tags_to_apply = [
        {'Key': 'LaunchDate', 'Value': current_date},
        {'Key': 'Environment', 'Value': 'Development'},
        {'Key': 'AutomationSource', 'Value': 'Lambda-AutoTag'}
    ]
    
    # 3. Inject tags into the newly spun-up infrastructure footprint
    try:
        ec2.create_tags(
            Resources=[instance_id],
            Tags=tags_to_apply
        )
        print(f"SUCCESS: Applied compliance tags to Instance {instance_id}: {tags_to_apply}")
    except Exception as e:
        print(f"CRITICAL: Failed to apply compliance tags to instance {instance_id}: {e}")

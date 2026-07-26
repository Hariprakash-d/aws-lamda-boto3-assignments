import boto3
import datetime
from botocore.exceptions import ClientError

# Configuration variables
SNS_TOPIC_ARN = "YOUR_SNS_TOPIC_ARN_HERE"  # <-- Paste your SNS Topic ARN from Step 1
COST_THRESHOLD = 0.01  # Set to $0.01 to guarantee a trigger during manual assignment testing

def lambda_handler(event, context):
    ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer endpoint is global (us-east-1)
    sns = boto3.client('sns')
    
    # 1. Dynamically compute the boundary window for Month-to-Date (MTD) tracking
    today = datetime.date.today()
    start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
    end_of_query = today.strftime('%Y-%m-%d')
    
    # Handle edge case where today is the 1st of the month
    if start_of_month == end_of_query:
        print("First day of the month detected. Skipping analysis due to zero baseline metrics.")
        return
        
    print(f"Querying MTD AWS cost metrics from {start_of_month} to {end_of_query}")
    
    # 2. Query data through the Cost Explorer API endpoint
    try:
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start_of_month, 'End': end_of_query},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        
        # Parse unblended pricing values out of JSON metric frames
        raw_amount = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
        current_spend = float(raw_amount)
        print(f"RETRIEVED AMOUNT: Current MTD Unblended Cost is ${current_spend:.2f}")
        
    except ClientError as e:
        print(f"CRITICAL: Failed to query Cost Explorer data: {e}")
        return

    # 3. Check threshold logic and execute conditional alerting pipelines
    if current_spend > COST_THRESHOLD:
        print(f"THRESHOLD EXCEEDED: ${current_spend:.2f} is greater than ${COST_THRESHOLD:.2f}. Dispatched alert email.")
        
        alert_message = (
            f"ALERT: Your AWS Month-to-Date spend has breached your safety threshold!\n\n"
            f"Current MTD Cost: ${current_spend:.2f}\n"
            f"Configured Threshold Limit: ${COST_THRESHOLD:.2f}\n"
            f"Reporting Target Window: {start_of_month} to {end_of_query}\n\n"
            f"This email was dispatched via automated Lambda analytics infrastructure."
        )
        
        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="⚠️ AWS Budget Breach Notification",
                Message=alert_message
            )
            print("SUCCESS: Alert message sent to SNS topic.")
        except ClientError as e:
            print(f"ERROR: Failed to push notification trace to SNS: {e}")
    else:
        print(f"OK: Current spend (${current_spend:.2f}) remains within safe limits (${COST_THRESHOLD:.2f}).")

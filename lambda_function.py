import os
import json
import urllib.request
import urllib.error
from datetime import datetime
import boto3

# Initialize AWS clients
# Boto3 automatically picks up credentials from the execution environment
sns_client = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'UptimeMonitorResults')
monitor_table = dynamodb.Table(table_name)

# Get environment variables
TARGET_URL = os.environ.get('TARGET_URL')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    """
    Pings the target URL, checks status, records data, and sends alerts on failure.
    """
    current_time = datetime.now().isoformat()
    status_code = 0
    latency_ms = -1
    status = 'FAIL'
    message = ''
    
    if not TARGET_URL:
        print("ERROR: TARGET_URL environment variable is not set.")
        return {'statusCode': 500, 'body': 'Configuration Error'}
        
    try:
        # Start timer
        start_time = datetime.now()
        
        # Perform the HTTP GET request
        # Setting a short timeout is good practice
        with urllib.request.urlopen(TARGET_URL, timeout=15) as response:
            status_code = response.getcode()
            
        # Calculate latency
        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        if 200 <= status_code < 400:
            status = 'SUCCESS'
            message = f"{TARGET_URL} is UP. Status Code: {status_code}. Latency: {latency_ms}ms"
            print(message)
        else:
            status = 'FAIL'
            message = f"ALERT: {TARGET_URL} returned a non-success status code: {status_code}"
            print(message)
            send_alert(message, status_code)
            record_downtime(current_time, status_code, latency_ms, message)

    except urllib.error.HTTPError as e:
        status_code = e.code
        status = 'FAIL'
        message = f"ALERT: {TARGET_URL} failed with HTTP Error: {status_code} - {e.reason}"
        print(message)
        send_alert(message, status_code)
        record_downtime(current_time, status_code, latency_ms, message)
        
    except urllib.error.URLError as e:
        status_code = 0 # 0 for network/DNS error
        status = 'FAIL'
        message = f"ALERT: {TARGET_URL} failed with URL Error (Network/DNS/Timeout): {e.reason}"
        print(message)
        send_alert(message, status_code)
        record_downtime(current_time, status_code, latency_ms, message)

    except Exception as e:
        status_code = -1
        status = 'FAIL'
        message = f"ALERT: An unexpected error occurred checking {TARGET_URL}: {str(e)}"
        print(message)
        send_alert(message, status_code)
        record_downtime(current_time, status_code, latency_ms, message)

    return {
        'statusCode': 200,
        'body': json.dumps({'status': status, 'url': TARGET_URL})
    }


def send_alert(alert_message, status_code):
    """Sends a notification to the configured SNS topic."""
    if not SNS_TOPIC_ARN:
        print("SNS_TOPIC_ARN is not set. Alert not sent.")
        return
        
    subject = f"Website Uptime Monitor Alert: {TARGET_URL} is DOWN ({status_code})"
    
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=alert_message,
            Subject=subject
        )
        print(f"SNS Alert sent to {SNS_TOPIC_ARN}")
    except Exception as e:
        print(f"Failed to send SNS alert: {str(e)}")


def record_downtime(timestamp, status_code, latency_ms, error_message):
    """Records the failure event in the DynamoDB table."""
    try:
        monitor_table.put_item(
            Item={
                'target_url': TARGET_URL,
                'timestamp': timestamp,
                'status_code': status_code,
                'latency_ms': latency_ms,
                'error_message': error_message
            }
        )
        print("Downtime event recorded in DynamoDB.")
    except Exception as e:
        print(f"Failed to record downtime in DynamoDB: {str(e)}")
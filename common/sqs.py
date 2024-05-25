import boto3
import json

# Configure the AWS SQS client
sqs = boto3.client('sqs', region_name='us-east-2')

def dropMessage(qURL, message, messageGroup, msgID):

    # Send response message to another SQS queue
    sqs.send_message(
        QueueUrl=qURL,
        MessageBody=json.dumps(message)
        # MessageGroupId=messageGroup,  # Required for FIFO queue
        # MessageDeduplicationId=msgID  # Ensure unique message ID for deduplication
    )


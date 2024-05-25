import boto3
import logging
import time
import subprocess
import json
from common.globals import Utility

# Configure logging
logging.basicConfig(filename='sqs_poller.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Log script start
logging.info('SQS Polling script started')

# Configure the AWS SQS client
sqs = boto3.client('sqs', region_name='us-east-2')

# SQS queue URLs
queue_url = Utility.PPT2IMAGE_REQUEST_Q_URL
response_queue_url = Utility.PPT2IMAGE_RESPONSE_Q_URL

def poll_sqs():
    while True:
        # Receive a message from SQS
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=20,
            MessageAttributeNames=['All'],
            VisibilityTimeout=30  # Visibility timeout in seconds
        )

        messages = response.get('Messages', [])
        if messages:
            for message in messages:
                try:
                    body = json.loads(message['Body'])
                    # Check if the message is NOT an SNS notification
                    if 'TopicArn' not in body:
                        # sns_message = json.loads(body['Message'])
                        subject = body.get('Subject', '')
                        message_id = body.get('MessageId', '')

                        logging.info(f"Processing message with subject: {subject} and ID: {message_id}")

                        if subject == '' or message_id == '':
                            logging.debug("Invalid message- no id found. passing through")
                            # Delete the message from the queue
                            continue

                        json_message = json.dumps(message)

                        # Your logic to trigger the Python program
                        # Replace 'your_program.py' with the path to your program
                        result = subprocess.run(['python', 'ppt2ImageProcessor.py', json_message])
                        
                        response_msg = {
                            'id': message_id,
                            'response': 'success' if result.returncode == 0 else 'failure'
                        }

                        if result.returncode == 0:
                            logging.info('ppt2ImageProcessor.py completed successfully')
                        else:
                            logging.error('ppt2ImageProcessor.py encountered an error')

                        # Send response message to another SQS queue
                        sqs.send_message(
                            QueueUrl=response_queue_url,
                            MessageBody=json.dumps(response_msg)
                            # MessageGroupId='responseGroup',  # Required for FIFO queue
                            # MessageDeduplicationId=message_id  # Ensure unique message ID for deduplication
                        )

                        # Delete the message from the queue
                        receipt_handle = message['ReceiptHandle']
                        sqs.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=receipt_handle
                        )
                except Exception as e:
                    logging.error(f"Error processing message: {e}")
                

                    # Delete the message from the queue to avoid 
                    # infinite loop
                    receipt_handle = message['ReceiptHandle']
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=receipt_handle
                    )

        # Sleep for a bit before polling again
        time.sleep(75)

if __name__ == '__main__':
    try:
        poll_sqs()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info('SQS Polling script ended')

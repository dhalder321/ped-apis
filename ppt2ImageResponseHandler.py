import boto3
import json
import time
from botocore.exceptions import ClientError, BotoCoreError
from common.globals import Utility

sqs = boto3.client('sqs')
queue_url = Utility.PPT2IMAGE_RESPONSE_Q_URL

def check_message_subject(target_subject, max_retries=15, delay=60):
    retries = 0
    while retries < max_retries:
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,  # Adjust based on how many messages you want to check at a time
                WaitTimeSeconds=20,  # Long polling
                MessageAttributeNames=['All'],
                VisibilityTimeout=30  # Visibility timeout in seconds
            )

            messages = response.get('Messages', [])
            for message in messages:
                try:
                    body = json.loads(message['Body'])
                    # Check if the message is an SNS notification
                    if 'TopicArn' not in body:
                        # sns_message = json.loads(body['Message'])
                        subject = body.get('id', '')
                        response = body.get('response', '')

                        if subject == target_subject and response == 'success':
                            print(f"Found message with subject: {subject}")
                            # Optionally, delete the message from the queue after processing
                            receipt_handle = message['ReceiptHandle']
                            sqs.delete_message(
                                QueueUrl=queue_url,
                                ReceiptHandle=receipt_handle
                            )
                            return True  # Found the message with the target subject

                    # # Delete the message even if it doesn't match the target subject to prevent reprocessing
                    # receipt_handle = message['ReceiptHandle']
                    # sqs.delete_message(
                    #     QueueUrl=queue_url,
                    #     ReceiptHandle=receipt_handle
                    # )
                except Exception as e:
                    print(f"Error processing message: {e}")

        except (ClientError, BotoCoreError) as e:
            print(f"Error receiving messages: {e}")
            retries += 1
            print(f"Retrying ({retries}/{max_retries})...")
            time.sleep(delay)

        retries += 1
        print(f"Retrying ({retries}/{max_retries})...")

    print("Max retries reached. Exiting.")
    return False


import boto3
import json
from common.globals import Utility
# from common.dotnet import convertPPT2Images 
import logging

def invokeLambdaFunction(functionName, payload):

    try:

        if Utility.EFS_LOCATION == Utility.Efs_Path:

            # Set up the Lambda client
            lambda_client = boto3.client('lambda')

            # Synchronous invocation
            response = lambda_client.invoke(
                FunctionName=functionName,
                Payload=payload,
                InvocationType= "RequestResponse",
                LogType="Tail"  # LogType can be "Tail" or "None"
            )

            # Asynchronous invocation
            # response = lambda_client.invoke(
            #     FunctionName=functionName,
            #     Payload=payload,
            #     InvocationType="Event"  # InvocationType can be "RequestResponse" (synchronous) or "Event" (asynchronous)
            # )

            # Get the response status code
            status_code = response['StatusCode']
            print("LAMBDA Status code ::" + str(status_code))

            # Get the response payload (if any)
            response_payload = response['Payload'].read()
            print("LAMBDA payload::" + str(response_payload))
            return json.loads(response_payload)
        
        else: # for local, call dotnet directly
            # return None
            # return convertPPT2Images(payload)
            return None
    except Exception as e:
        logging.error(str(e))
        return None


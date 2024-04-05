import boto3
import json
from common.globals import Utility
from common.dotnet import convertPPT2Images 


def invokeLambdaFunction(functionName, payload):

    if Utility.EFS_LOCATION == Utility.Efs_Path:

        # Set up the Lambda client
        lambda_client = boto3.client('lambda')

        # Synchronous invocation
        # response = lambda_client.invoke(
        #     FunctionName=function_name,
        #     Payload=payload,
        #     LogType="Tail"  # LogType can be "Tail" or "None"
        # )

        # Asynchronous invocation
        response = lambda_client.invoke(
            FunctionName=functionName,
            Payload=payload,
            InvocationType="Event"  # InvocationType can be "RequestResponse" (synchronous) or "Event" (asynchronous)
        )

        # Get the response status code
        status_code = response['StatusCode']
        print(status_code)

        # Get the response payload (if any)
        response_payload = str(response['Payload'].read())
        print(response_payload)
        return response_payload
    
    else: # for local, call dotnet directly
        # return None
        return convertPPT2Images(payload)


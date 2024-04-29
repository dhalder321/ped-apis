import os
import logging
import json, uuid
from common.globals import Utility, DBTables
from common.s3File import uploadFile 
from datetime import datetime, timezone
from common.db import DBManager
from common.globals import PED_Module


############################################################
############################################################
#return error codes:
# 1001 - missing input in the request
# 2001 - more than one user found
# 2002 - no user found
# 2003 - login status update to db failed
# 5001 - Method level error
############################################################

def verifyEmailVerificationCode(event, context):

    print(event)
    logging.debug(event)

    # process OPTIONS method
    origin = None
    if 'headers' in event and event['headers'] != '' and \
          'origin' in event['headers'] and event['headers']['origin'] != '':
        origin = event['headers']['origin']

    #process OPTIONS method
    if 'httpMethod' in event and event['httpMethod'] == 'OPTIONS':
      return Utility.generateResponse(200, {}, origin)

    #process only POST methods
    if 'httpMethod' in event and event['httpMethod'] == 'POST':

        if 'body' not in event or event['body'] is None:
            return Utility.generateResponse(400, {
                        'errorCode': "999",
                        'error': 'No request object found',
                    }, origin)
        
        body = json.loads(event['body'])

        try:

            #initiate DB modules
            PED_Module.initiate()

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "verifyEmailVerificationCode")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            email = body["email"] if 'email' in body else None
            emailCode = body["emailCode"] if 'emailCode' in body else None
            requesttimeinUTC = body["requesttimeinUTC"] if 'requesttimeinUTC' in body else None
            
            if email is None or emailCode is None or len(emailCode) != 6:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1001",
                        'error': 'invalid email or verification code provided',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response

            # check for matching email and verification code
            retVal = Utility.verifyEmailVerificationCode(email, emailCode)
            if retVal is None:
                response = Utility.generateResponse(500, {
                            'transactionId' : tran_id,
                            'errorCode': "2001",
                            'error': 'verification code could not be verified',
                            'AnswerRetrieved': False
                        }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response
            
            if retVal == False:
                response =  Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': 'failure',
                                    'AnswerRetrieved': True
                                }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response
            
            # Return the response in JSON format
            response =  Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': 'success',
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, "-1", \
                                                   f"Error in verifyEmailVerificationCode Function: {str(e)}"))
            logging.error("Stack Trace:", exc_info=True)
            
            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "5001",
                                    'error': 'Error processing your request',
                                    'AnswerRetrieved': False
                                }, origin)
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        
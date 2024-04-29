import random
import string
import logging
import json, uuid
from common.globals import Utility, DBTables
from common.s3File import uploadFile 
from pathlib import Path
from datetime import datetime, timezone
from common.db import DBManager
from docx import Document
from htmldocx import HtmlToDocx
from common.globals import PED_Module

############################################################
############################################################
#return error codes:
# 1001 - missing input in the request
# 2001 - user has not signed up
# 2002 - unique access key cound not be generated 
# 2003 - access key generation status update to db failed
# 5001 - Method level error
############################################################

def generateEmailVerificationCode(event, context):

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
                    })
        
        body = json.loads(event['body'])

        try:
            #initiate DB modules
            PED_Module.initiate()

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "generateEmailVerificationCode")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            email = body["email"] if 'email' in body else None
            requesttimeinUTC = body["requesttimeinUTC"] if 'requesttimeinUTC' in body else None
            
            if email is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1001",
                        'error': 'Missing email or verification code in the verification code request',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response
            
            # check for existing email
            userRecord = DBManager.getDBItemByIndex(DBTables.User_Table_Name, "email", "email-index", email)
            if userRecord is not None and len(userRecord) > 0:
                # Return a 400 Bad Request response if email is already present
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'Email is already present',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response

            # send email verification code through email 
            retVal = Utility.sendEmailConfirmationCodeInEmail(email)
            if retVal == False:
                # Return a 400 Bad Request response if email is already present
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'Email could not be sent',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response

            # Return the response in JSON format
            response =  Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': 'success',
                                    'AnswerRetrieved': True
                                })
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, "-1", \
                                                   f"Error in generateEmailVerificationCode Function: {str(e)}"))
            logging.error("Stack Trace:", exc_info=True)
            
            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "5001",
                                    'error': 'Error processing your request',
                                    'AnswerRetrieved': False
                                })
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response


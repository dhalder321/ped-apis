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

def loginUserWithAccessKey(event, context):

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
            activityId = Utility.logUserActivity(body, "loginUserWithAccessKey")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            # "asseccKey": "dhalder@gmail.com",
            # "transactionId": "8736423hk2j3483",
            # "requesttimeinUTC": "3/14/2024 21:18" 

            asseccKey = body["asseccKey"] if 'asseccKey' in body else None
            requesttimeinUTC = body["requesttimeinUTC"] if 'requesttimeinUTC' in body else None
            
            if asseccKey is None or len(asseccKey) != 6:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1001",
                        'error': 'invalid access key provided',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response

            # check for signedup user
            userRecord = DBManager.getDBItemByIndex(DBTables.User_Table_Name, \
                                                    "accessKey", "accessKey-index", asseccKey)
            
            if userRecord is not None:
                if len(userRecord) > 1:
                    # Return a 400 Bad Request response if email is already present
                    response = Utility.generateResponse(400, {
                            'transactionId' : tran_id,
                            'errorCode': "2001",
                            'error': 'More than one user found',
                            'AnswerRetrieved': False
                        }, origin)
                    Utility.updateUserActivity(str(activityId), "-1", response)
                    return response
                elif len(userRecord) <= 0:
                    # Return a 400 Bad Request response if email is already present
                    response = Utility.generateResponse(400, {
                            'transactionId' : tran_id,
                            'errorCode': "2002",
                            'error': 'no user found',
                            'AnswerRetrieved': False
                        }, origin)
                    Utility.updateUserActivity(str(activityId), "-1", response)
                    return response
            
            userid = str(userRecord[0]['userid'])
            email = userRecord[0]['email']

            # update record in user table for last login
            retVal = DBManager.updateRecordInDynamoTable(DBTables.User_Table_Name, \
                                                                    "userid",userid, \
                                                                    "email", email, \
                                                                    {
                "accessBy": "accesskey",
                "loginStatus": "loggedin",
                "lastLoginTimeUTC": datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S"),
            })

            if retVal is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2003",
                                    'error': 'Error processing your request',
                                }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response

            # Return the response in JSON format
            response =  Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'userid': userid,
                                    'firstName': userRecord[0]['firstName'],
                                    'lastName': userRecord[0]['lastName'],
                                    'email': email,
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in loginUserWithAccessKey Function: {str(e)}")
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

        
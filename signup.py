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
# 2001 - Email is already present
# 2002 - error adding new user in db 
# 5001 - Method level error
############################################################
def signupNewUser(event, context):

    body = json.loads(event['body'])

    try:

        #initiate DB modules
        PED_Module.initiate()

        #log user and transaction details
        activityId = Utility.logUserActivity(body, "signupNewUser")

        tran_id = body["transactionId"]
        if tran_id is None:
            tran_id = str(uuid.uuid1())
    
        # Parse the incoming JSON payload
        # "firstName": "Chandrasekhar",
        # "lastName": "Raman",
        # "email": "cvraman@gmail.com",
        # "pwdEn": "^%*&$(*&!@dskjvkds)", 
        # "transactionId": "8736423hk2j3483",
        # "requesttimeinUTC": "3/14/2024 21:18"    

        firstName = body["firstName"] if 'firstName' in body else ""
        lastName = body["lastName"] if 'lastName' in body else ""
        email = body["email"] if 'email' in body else None
        pwdEn = body["pwdEn"] if 'pwdEn' in body else None
        requesttimeinUTC = body["requesttimeinUTC"] if 'requesttimeinUTC' in body else None
        
        if email is None or pwdEn is None:
            # Return a 400 Bad Request response if input is missing
            response = Utility.generateResponse(400, {
                    'transactionId' : tran_id,
                    'errorCode': "1001",
                    'error': 'Missing email in the signup request',
                    'AnswerRetrieved': False
                })
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        # check for avaialble email
        userRecord = DBManager.getDBItemByIndex(DBTables.User_Table_Name, "email", "email-index", email)
        if userRecord is not None and len(userRecord) > 0:
            # Return a 400 Bad Request response if email is already present
            response = Utility.generateResponse(400, {
                    'transactionId' : tran_id,
                    'errorCode': "2001",
                    'error': 'Email is already present',
                    'AnswerRetrieved': False
                })
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        # add record in user table
        retVal = DBManager.addRecordInDynamoTableWithAutoIncrKey(DBTables.User_Table_Name, \
                                                                 "staticIndexColumn", "userid",\
                                                                 "staticIndexColumn-userid-index",  \
                                                                  {
            "staticIndexColumn": 99, #for global sec. index column
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "pwdEn": pwdEn,
            "userCreationDateTime": requesttimeinUTC,
        })

        if retVal is None:
            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                'transactionId' : tran_id,
                                'errorCode': "2002",
                                'error': 'Error processing your request',
                            })
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        # Return the response in JSON format
        response =  Utility.generateResponse(200, {
                                'transactionId' : tran_id,
                                'userid': retVal,
                                'AnswerRetrieved': True
                            })
        Utility.updateUserActivity(str(activityId), "-1", response)
        return response

    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in signupNewUser Function: {str(e)}")
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

       
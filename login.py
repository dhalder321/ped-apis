import os
import logging
import json, uuid
from common.globals import Utility, DBTables
from common.s3File import uploadFile 
from datetime import datetime, timezone
from common.db import DBManager
from common.globals import PED_Module

# "loginUserWithemail", "loginUserWithKey"
def loginUserWithemail(event, context):

    body = json.loads(event['body'])

    try:

        #initiate DB modules
        PED_Module.initiate()

        #log user and transaction details
        activityId = Utility.logUserActivity(body, "loginUserWithemail")

        tran_id = body["transactionId"]
        if tran_id is None:
            tran_id = str(uuid.uuid1())
    
        # Parse the incoming JSON payload
        # "email": "cvraman1@gmail.com",
        # "pwdEn": "^%*&$(*&!@dskjvkds)", 
        # "transactionId": "8736423hk2j3483",
        # "requesttimeinUTC": "3/14/2024 21:18"  

        email = body["email"] if 'email' in body else None
        pwdEn = body["pwdEn"] if 'pwdEn' in body else None
        requesttimeinUTC = body["requesttimeinUTC"] if 'requesttimeinUTC' in body else None
        
        if email is None or pwdEn is None:
            # Return a 400 Bad Request response if input is missing
            response = Utility.generateResponse(400, {
                    'transactionId' : tran_id,
                    'error': 'Missing email or password in the login request',
                    'AnswerRetrieved': False
                })
            Utility.updateUserActivity(str(activityId), "-1", response)
            return response

        # check for signedup user
        #TO DO:        table_name='ped-users',
        # partition_key_name="userid",
        # partition_key_value="3",
        # sort_key_name="email",
        # sort_key_value="dhalder@gmail.com",
        # filter_expression='pwdEn = :value',
        # value="^%*&$(*&!@dskjvkds)", 
        # projection_expression='userid, firstName, lastName',
        # index_name="email-index")
    
        userRecord = DBManager.getDBItems(table_name=DBTables.User_Table_Name, \
                                          sort_key_name="email", sort_key_value=email, \
                                          filter_expression= "pwdEn = :value", \
                                          value = pwdEn, \
                                          projection_expression="userid, firstName, lastName", \
                                          index_name="email-index")
        
        if userRecord is not None:
            if len(userRecord) > 1:
                # Return a 400 Bad Request response if email is already present
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'error': 'More than one users found',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response
            elif len(userRecord) <= 0:
                 # Return a 400 Bad Request response if email is already present
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'error': 'no user found',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response
        
        userid = str(userRecord[0]['userid'])

        # update record in user table for last login
        retVal = DBManager.updateRecordInDynamoTable(DBTables.User_Table_Name, \
                                                                  "userid",userid,
                                                                  "email", email, \
                                                                  {
            "accessBy": "email+password",
            "lastLoginTimeUTC": datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S"),
        })

        #IGNORE THE ERROR TO LOG LASTLOGIN TIME
        # if retVal is None:
        #     # Return a 500 server error response
        #     response = Utility.generateResponse(500, {
        #                         'transactionId' : tran_id,
        #                         'Error': 'Error processing your request',
        #                     })
        #     Utility.updateUserActivity(str(activityId), "-1", response)
        #     return response

        # Return the response in JSON format
        response =  Utility.generateResponse(200, {
                                'transactionId' : tran_id,
                                'userid': userid,
                                'firstName': userRecord[0]['firstName'],
                                'lastName': userRecord[0]['lastName'],
                                'AnswerRetrieved': True
                            })
        Utility.updateUserActivity(str(activityId), "-1", response)
        return response

    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in loginUserWithemail Function: {str(e)}")
        logging.error("Stack Trace:", exc_info=True)
        
        # Return a 500 server error response
        response = Utility.generateResponse(500, {
                                'transactionId' : tran_id,
                                'Error': 'Error processing your request',
                                'AnswerRetrieved': False
                            })
        Utility.updateUserActivity(str(activityId), "-1", response)
        return response

       
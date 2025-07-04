
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

def getAccessKey(event, context):

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
            env = ''
            stageVariables = event['stageVariables'] if 'stageVariables' in event else None
            if stageVariables is not None:
                env = stageVariables['Environment'] if 'Environment' in stageVariables else ""
            PED_Module.initiate(env)

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "getAccessKey")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            # "userid": 2,
            # "transactionId": "8736423hk2j3483",
            # "requesttimeinUTC": "3/14/2024 21:18" 

            userid = body["userid"] if 'userid' in body else None
            requesttimeinUTC = body["requesttimeinUTC"] if 'requesttimeinUTC' in body else None
            
            if userid is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1001",
                        'error': 'Missing userid in the access key request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # check for avaialble access key
            userRecord = DBManager.getDBItemByPartitionKey(DBTables.User_Table_Name, \
                                                                    "userid", int(userid))
            if userRecord is None:
                # Return a 400 Bad Request response if email is already present
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'user has not signed up',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # return the access key if available
            if 'accessKey' in userRecord and userRecord['accessKey'] is not None \
                and len(userRecord['accessKey']) == 6:
                # Return access key
                response = Utility.generateResponse(200, {
                        'transactionId' : tran_id,
                        'accessKey': userRecord['accessKey'],
                        'AnswerRetrieved': True
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # create a new and unique access key
            accesskey = Utility.generateAccessCode()

            if accesskey is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2002",
                                    'error': 'unique access key cound not be generated',
                                    'AnswerRetrieved': True
                                }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # update record in user table
            retVal = DBManager.updateRecordInDynamoTable(DBTables.User_Table_Name, \
                                                                    "userid", userid,\
                                                                    "", "", \
                                                                    {
                "accessKey": accesskey,
                "accessKeyCreationTimeUTC": datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S"),
            })

            if retVal is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2003",
                                    'error': 'Error processing your request',
                                    'AnswerRetrieved': True
                                }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # Return the response in JSON format
            response =  Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'accessKey': accesskey,
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                                   f"Error in getAccessKey Function: {str(e)}"))
            logging.error("Stack Trace:", exc_info=True)
            
            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "5001",
                                    'error': 'Error processing your request',
                                    'AnswerRetrieved': False
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response



    
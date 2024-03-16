import random
import string
import os
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


def getAccessKey(event, context):

    body = json.loads(event['body'])

    try:
        #initiate DB modules
        PED_Module.initiate()

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
                    'error': 'Missing userid in the access key request',
                    'AnswerRetrieved': False
                })
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        # check for avaialble access key
        userRecord = DBManager.getDBItemByPartitionKey(DBTables.User_Table_Name, \
                                                                "userid", int(userid))
        if userRecord is None:
            # Return a 400 Bad Request response if email is already present
            response = Utility.generateResponse(400, {
                    'transactionId' : tran_id,
                    'error': 'user has not signed up',
                    'AnswerRetrieved': False
                })
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
                })
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        # create a new and unique access key
        accesskey = generateAccessCode()

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
                                'Error': 'Error processing your request',
                                'AnswerRetrieved': True
                            })
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        # Return the response in JSON format
        response =  Utility.generateResponse(200, {
                                'transactionId' : tran_id,
                                'accessKey': accesskey,
                                'AnswerRetrieved': True
                            })
        Utility.updateUserActivity(str(activityId), userid, response)
        return response

    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in getAccessKey Function: {str(e)}")
        logging.error("Stack Trace:", exc_info=True)
        
        # Return a 500 server error response
        response = Utility.generateResponse(500, {
                                'transactionId' : tran_id,
                                'Error': 'Error processing your request',
                                'AnswerRetrieved': False
                            })
        Utility.updateUserActivity(str(activityId), userid, response)
        return response


def generateAccessCode():
    characters = string.ascii_uppercase + string.digits
    while True:
        unique_code = ''.join(random.choices(characters, k=6))
        # Check if the generated code is unique 
        if isCodeUnique(unique_code):
            return unique_code

def isCodeUnique(code):
    
    try:
        record = DBManager.getDBItemByIndex(DBTables.User_Table_Name, "accessKey", "accessKey-index", code)

        if record is not None and len(record) > 0 \
            and 'accessKey' in record and record['accessKey'] == code :
            return False
        return True
    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in isCodeUnique Function: {str(e)}")
        logging.error("Stack Trace:", exc_info=True)
        return False
 
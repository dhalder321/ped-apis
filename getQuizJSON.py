
import logging
import json, uuid
from pathlib import Path
from datetime import datetime, timezone
from common.db import DBManager
from common.s3File import readFile, createS3PresignedURL
from common.globals import Utility, PED_Module, DBTables
from common.prompts import Prompt
from common.model import getBulkModelResponses

from transform.inputProcessor import inputProcessor 
from transform.transformationHandler import transformationHandler 
from transform.outputGenerator import outputGenerator 
import asyncio


############################################################
############################################################
#return error codes:
#  999 - No request object found
# 1001 - missing user id in the request
# 1002 - missing input in the request
# 2001 - text could not be retrieved from provided  file
# 2002 - provided file content could not be saved locally
# 2003 - text is too short for any transformation
# 2004 - model response could not be obtained
# 2005 - prompt could not be retrieved
# 2006 - document could not be stored
# 2007 - document record could not be updated in database
# 5001 - Method level error
############################################################
def getQuizJSON(event, context):

    # print(event)
    logging.debug(event)

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
            activityId = Utility.logUserActivity(body, "getQuizJSON")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            priorTranIds = body["priorTranIds"] if 'priorTranIds' in body else ""
            quizFileId = body["quizFileId"] if 'quizFileId' in body else None
            userid = body["userid"]  if "userid" in body else None

            if userid is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1001",
                        'error': 'Missing userid or quiz file id in the request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), "-1", response)
                return response

            # check for valid and logged in user
            # CheckLoggedinUser(userid)

            # if priorTranIds is not empty, locate the privious 
            # successful transactions
            if priorTranIds != "":
                priorResponse = Utility.handlePriorTransactionIds(userid, priorTranIds)
                if priorResponse is not None:
                    return priorResponse 
            
            if  quizFileId is None or quizFileId == '':
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1002",
                        'error': 'Missing quiz file id in the request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # check the record
            record = DBManager.getDBItemByPartitionKey(DBTables.UserFiles_Table_Name, 
                                                    "fileid", int(quizFileId))
            
            if record is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'provided file id not found',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            if 's3bucketName' not in record or 's3Filelocation' not in record or \
                    record['s3bucketName'] == '' or record['s3Filelocation'] == '' or \
                        'userid' not in record or record['userid'] == '' :
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2004",
                        'error': 'file location not found or userid not valid in the db',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # check for matching userid - No way we can send one user's file to another
            if 'userid' not in record or str(record['userid']) != userid:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2005",
                        'error': 'user id does not match',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # get the quiz JSON from s3 qzx file
            s3fileLocation = Utility.S3OBJECT_NAME_FOR_USER_FILES + "/" + Utility.ENVIRONMENT
            s3filePath = s3fileLocation + record['s3Filelocation']
            qzxFileContent = readFile(record['s3bucketName'], s3filePath)

            if qzxFileContent is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2006",
                        'error': 'file content could not be retrieved',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # Return the response in JSON format
            response = Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': qzxFileContent,
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                                   message=f"Error in getQuizJSON Function: {str(e)}"))
            logging.error("Stack Trace:", exc_info=True)
            
            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "5001",
                                    'error': 'Error processing your request',
                                    'AnswerRetrieved': False
                                }, origin)
            Utility.updateUserActivity(str(activityId), -1, response)
            return response




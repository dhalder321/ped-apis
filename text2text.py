import logging
import os
import json, uuid
from pathlib import Path
from datetime import datetime, timezone
from common.db import DBManager
from docx import Document
from htmldocx import HtmlToDocx
from common.prompts import Prompt
from common.model import retryModelForOutputType
from common.globals import Utility, PED_Module, DBTables
from transform.inputProcessor import inputProcessor 
from transform.transformationHandler import transformationHandler 
from transform.outputGenerator import outputGenerator 


############################################################
############################################################
#return error codes:
#  999 - No request object found
# 1001 - missing user id in the request
# 1002 - missing input in the request
# 2001 - text could not be retrieved from provided  file
# 2002 - model response could not be obtained
# 2003 - prompt could not be retrieved
# 2004 - document could not be stored
# 2005 - document record could not be updated in database
# 5001 - Method level error
############################################################
def generateDocumentFromText(event, context):

    print(event)
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
            env = ''
            stageVariables = event['stageVariables'] if 'stageVariables' in event else None
            if stageVariables is not None:
                env = stageVariables['Environment'] if 'Environment' in stageVariables else ""
            PED_Module.initiate(env)

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "generateDocumentFromDocument")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            priorTranIds = body["priorTranIds"] if 'priorTranIds' in body else ""
            text = body["text"] if 'text' in body else None
            renderingType = body["renderingType"]  if "renderingType" in body else None
            instruction = body["instruction"]  if "instruction" in body else None
            userid = body["userid"]  if "userid" in body else None

            if userid is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1001",
                        'error': 'Missing userid in the request',
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
            
            if text is None or renderingType is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1002",
                        'error': 'Missing text or rendering type in the request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # check for minimum length of the text- min 400 chars
            if len(text) < 400:
                
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'text is too short for any transformation',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # transform the input text 
            newInst = instruction + " " + Utility.PROMPT_EXTENSION_4_HTML_OUTPUT \
                if instruction is not None else Utility.PROMPT_EXTENSION_4_HTML_OUTPUT
            inputs = {
                # "wordCount": wordCount,
                # "renderingType": renderingType,
                "instruction": newInst
            }
            trmsText = transformationHandler.transformText(text, renderingType, **inputs)

            if trmsText is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'model response could not be obtained',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            if trmsText == "PROMPT_NOT_GENERATED":
                
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2003",
                        'error': 'prompt could not be retrieved',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # save html text in word document
            # upload the document to S3 and generate pre-signed URL
            localDocFileLocation = str(Path(Utility.EFS_LOCATION, userid))
            datetimestring = datetime.now().replace(tzinfo=timezone.utc).strftime("%m%d%Y%H%M%S")
            datetimeFormattedString = datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
            localDocFileName = "Document_"+ tran_id + "_" + datetimestring + ".docx"
            localDocFilePath = str(Path(localDocFileLocation, localDocFileName))
            s3filePath = "/" + userid + "/" + localDocFileName
            presignedURL = outputGenerator.storeOutputFile(trmsText, "DOC", "HTML", \
                                                           localDocFileName, localDocFileLocation,\
                                                            s3filePath)
            
            if presignedURL is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2004",
                                    'error': 'document could not be stored',
                                }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # add record in userfiles table
            retVal = DBManager.addRecordInDynamoTableWithAutoIncrKey(DBTables.UserFiles_Table_Name, \
                                                                    "staticIndexColumn", "fileid",\
                                                                    "staticIndexColumn-fileid-index",  \
                                                                    {
                "userid": int(userid),
                "transactionId": tran_id,
                "staticIndexColumn": 99, #for global sec. index column
                "fileName": localDocFileName,
                "s3Filelocation": s3filePath,
                "s3bucketName": Utility.S3BUCKE_NAME,
                "initials3PresignedURLGenerated": presignedURL,
                "fileCreationDateTime": datetimeFormattedString,
                "fileType": "docx",
                "fileStatus": "complete",
                "user-fileName": "",
            })

            if retVal is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2005",
                                    'error': 'document record could not be updated in database',
                                }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # delete the local files and folders
            Path(localDocFilePath).unlink()
            localFolder = Path(localDocFileLocation)
            if localFolder is not None and not any(localFolder.iterdir()):
                localFolder.rmdir()

            # Return the response in JSON format
            response = Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': presignedURL,
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                                   message=f"Error in generateDocumentFromDocument Function: {str(e)}"))
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

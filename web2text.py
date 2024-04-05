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
# 2001 - text could not be retrieved from provided presentation file
# 2002 - provided file content could not be saved locally
# 2003 - text is too short for any transformation
# 2004 - model response could not be obtained
# 2005 - prompt could not be retrieved
# 2006 - document could not be stored
# 2007 - document record could not be updated in database
# 5001 - Method level error
############################################################
def generateDocumentFromWebContent(event, context):

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
            PED_Module.initiate()

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "generateDocumentFromPresentation")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            url = body["url"] if 'url' in body else None
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
            
            

            # get the text from the ppt content
            inputValues = {
                            "url": url
                            }
            retVal = inputProcessor.processInput("webURL", **inputValues)
            
            # get the text from ppt file
            if retVal is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'text could not be retrieved from provided presentation file',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # Create the local directory if it does not exist
            if retVal == "INVALID_URL":

                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'Invalid URL provided',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            print(str(len(retVal)) + "::" + retVal)
            # check for minimum length of the text- min 400 chars
            if len(retVal) < 400:
                
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2003",
                        'error': 'text is too short for any transformation',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # check for max length of the text- max 10500 chars
            if len(retVal) > 10500:
                
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2004",
                        'error': 'text is too large for processing',
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
            trmsText = transformationHandler.transformText(retVal, renderingType, **inputs)

            if trmsText is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2005",
                        'error': 'model response could not be obtained',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            if trmsText == "PROMPT_NOT_GENERATED":
                
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2006",
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
                                    'errorCode': "2007",
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
                                    'errorCode': "2008",
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
            logging.error(f"Error in generateDocumentFromPresentation Function: {str(e)}")
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

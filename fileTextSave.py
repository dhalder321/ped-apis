import os
import logging
import json, uuid
from common.globals import Utility, DBTables
from pathlib import Path
from datetime import datetime, timezone
from common.db import DBManager
from common.globals import PED_Module

############################################################
############################################################
#return error codes:
#  999 - No request object found
# 1001 - missing text to save in the request
# 2001 - file content could not be saved locally
# 2002 - user file entry addition failed
# 5001 - Method level error
############################################################


def saveDocumentFile(event, context):
     
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

            #check user id logged in and userid is valid
            #TODO:

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "saveDocumentFile")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            textInHTML = body["text"] if 'text' in body else None
            fileContentInBase64 = body["fileContentInBase64"] if 'fileContentInBase64' in body else None

            userid = body["userid"] if 'userid' in body else None
            lang = body["lang"] if 'lang' in body else None
            
            if textInHTML is None and fileContentInBase64 is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1001",
                        'error': 'Missing file content and text to save in the request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            #save the text from HTML in docx format
            localFileLocation = str(Path(Utility.EFS_LOCATION, userid))
            datetimestring = datetime.now().replace(tzinfo=timezone.utc).strftime("%m%d%Y%H%M%S")
            datetimeFormattedString = datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
            localFileName = "DocumentFile_"+ tran_id + "_" + datetimestring + ".docx"
            localFilePath = str(Path(localFileLocation, localFileName))
            #print('localFilePath: ' + localFilePath)
            
            # upload the document in s3
            s3filePath = "/" + userid + "/" + localFileName
            presignedURL = ''
            
            # for html content
            if textInHTML is not None and textInHTML != '':
                presignedURL = Utility.uploadDocumentinHTMLtoS3(textInHTML, localFileName, \
                                                            localFileLocation, s3filePath)
            # for base64 content    
            elif fileContentInBase64 is not None and fileContentInBase64 != '':
                presignedURL = Utility.uploadDocumentinBase64toS3(fileContentInBase64, localFileName, \
                                                            localFileLocation, s3filePath)
            
            if presignedURL is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'File content could not be saved locally',
                        'AnswerRetrieved': False
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
                "fileName": localFileName,
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
                                    'errorCode': "2002",
                                    'error': 'file record could not be saved in db',
                                }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            #delete temporary files and folders
            Path(localFilePath).unlink()
            localFolder = Path(localFileLocation)
            if not any(localFolder.iterdir()):
                localFolder.rmdir()

            # Return the response in JSON format
            response =  Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': presignedURL,
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in saveDocumentFile Function: {str(e)}")
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

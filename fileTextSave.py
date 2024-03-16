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

def saveDocumentFile(event, context):
     
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
        userid = body["userid"] if 'userid' in body else None
        lang = body["lang"] if 'lang' in body else None
        
        if textInHTML is None:
            # Return a 400 Bad Request response if input is missing

            response = Utility.generateResponse(400, {
                    'transactionId' : tran_id,
                    'error': 'Missing text to save in the request',
                    'AnswerRetrieved': False
                })
            Utility.updateUserActivity(str(activityId), userid, response)
            return response
            

        #save the text from HTML in docx format
        localFileLocation = str(Path(Utility.EFS_LOCATION, userid))
        datetimestring = datetime.now().replace(tzinfo=timezone.utc).strftime("%m%d%Y%H%M%S")
        datetimeFormattedString = datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
        localFileName = "DocumentFile_"+ tran_id + "_" + datetimestring + ".docx"
        localFilePath = str(Path(localFileLocation, localFileName))
        #print('localFilePath: ' + localFilePath)
        
        # Create the local directory if it does not exist
        isExist = os.path.exists(localFileLocation)
        if not isExist:    
            os.makedirs(localFileLocation) 
        document = Document()
        parser =  HtmlToDocx()
        parser.add_html_to_document(textInHTML, document)
        document.save(localFilePath)

        #upload to S3
        s3fileLocation = Utility.S3OBJECT_NAME_FOR_USER_FILES + "/" + Utility.ENVIRONMENT
        s3filePath = s3fileLocation + "/" + userid + "/" + localFileName
        print("s3filePath:" + s3filePath)
        presignedURL = uploadFile(localFilePath, Utility.S3BUCKE_NAME, s3filePath)

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

        if retVal == False:
            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                'transactionId' : tran_id,
                                'Error': 'Error processing your request',
                            })
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        #delete temporary files
        Path(localFilePath).unlink()

        # Return the response in JSON format
        response =  Utility.generateResponse(200, {
                                'transactionId' : tran_id,
                                'Response': presignedURL,
                                'AnswerRetrieved': True
                            })
        Utility.updateUserActivity(str(activityId), userid, response)
        return response

    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in saveDocumentFile Function: {str(e)}")
        logging.error("Stack Trace:", exc_info=True)
        
        # Return a 500 server error response
        response = Utility.generateResponse(500, {
                                'transactionId' : tran_id,
                                'Error': 'Error processing your request',
                                'AnswerRetrieved': False
                            })
        Utility.updateUserActivity(str(activityId), userid, response)
        return response

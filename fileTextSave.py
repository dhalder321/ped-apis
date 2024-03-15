import os
import logging
import json, uuid
from common.globals import Utility
from common.globals import Document, HTML2Document
from common.s3File import uploadFile 
from pathlib import Path
from datetime import datetime
from common.db import DBManager

def saveDocumentFile(event, context):
     
    body = json.loads(event['body'])

    try:

        #check user id logged in and userid is valid
        #TODO:

        #log user and transaction details
        Utility.logUserActivity(body, "saveDocumentFile")

        tran_id = body["transactionId"]
        if tran_id is None:
            tran_id = str(uuid.uuid1())
    
        # Parse the incoming JSON payload
        textInHTML = body["text"] if 'text' in body else None
        userid = body["userid"] if 'userid' in body else None
        lang = body["lang"] if 'lang' in body else None
        
        if textInHTML is None:
            # Return a 400 Bad Request response if input is missing
            return Utility.generateResponse(400, {
                    'transactionId' : tran_id,
                    'error': 'Missing text to save in the request',
                    'AnswerRetrieved': False
                })
            

        #save the text from HTML in docx format
        localFileLocation = str(Path(Utility.EFS_LOCATION, userid))
        datetimestring = datetime.now().strftime("%m%d%Y%H%M%S")
        datetimeFormattedString = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        localFileName = "DocumentFile_"+ tran_id + "_" + datetimestring + ".docx"
        localFilePath = str(Path(localFileLocation, localFileName))
        #print('localFilePath: ' + localFilePath)
        
        # Create the local directory if it does not exist
        isExist = os.path.exists(localFileLocation)
        if not isExist:    
            os.makedirs(localFileLocation) 
        document = Document()
        parser = HTML2Document(document)
        parser.feed(textInHTML)
        document.save(localFilePath)

        #upload to S3
        s3fileLocation = Utility.S3OBJECT_NAME_FOR_USER_FILES + "/" + Utility.ENVIRONMENT
        s3filePath = s3fileLocation + "/" + userid + "/" + localFileName
        print("s3filePath:" + s3filePath)
        presignedURL = uploadFile(localFilePath, Utility.S3BUCKE_NAME, s3filePath)

        #add record in userfiles table
        #TODO:
        # retVal = DBManager.addRecordInDynamoTableWithAutoIncrKey("ped-userfiles", "fileid", "fileid-index",{
        #     "userid": userid,
        #     "transactionId": tran_id,
        #     "fileName": localFileName,
        #     "s3Filelocation": s3filePath,
        #     "s3bucketName": Utility.S3BUCKE_NAME,
        #     "initials3PresignedURLGenerated": presignedURL,
        #     "fileCreationDateTime": datetimeFormattedString,
        #     "fileType": "docx",
        #     "fileStatus": "complete",
        #     "user-fileName": "",
        # })

        # if retVal == False:
        #     # Return a 500 server error response
        #     return Utility.generateResponse(500, {
        #                         'transactionId' : tran_id,
        #                         'Error': 'Error processing your request',
        #                     })

        #delete temporary files
        Path(localFilePath).unlink()

        # Return the response in JSON format
        return Utility.generateResponse(200, {
                                'transactionId' : tran_id,
                                'Response': presignedURL,
                                'AnswerRetrieved': True
                            })

    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in saveDocumentFile Function: {str(e)}")
        logging.error("Stack Trace:", exc_info=True)
        
        # Return a 500 server error response
        return Utility.generateResponse(500, {
                                'transactionId' : tran_id,
                                'Error': 'Error processing your request',
                                'AnswerRetrieved': False
                            })
        

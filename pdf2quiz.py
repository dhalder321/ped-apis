
import logging
import os
import json, uuid
from pathlib import Path
from datetime import datetime, timezone
from common.db import DBManager
from common.file import deleteDirWithFiles
from docx import Document
from htmldocx import HtmlToDocx
from common.prompts import Prompt
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
# 2002 - provided file content could not be saved locally
# 2003 - text is too short for any transformation
# 2004 - model response could not be obtained
# 2005 - prompt could not be retrieved
# 2006 - document could not be stored
# 2007 - document record could not be updated in database
# 5001 - Method level error
############################################################
def generateQuizFromPDF(event, context):

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
        foldertoDelete = ''
        try:

            #initiate DB modules
            env = ''
            stageVariables = event['stageVariables'] if 'stageVariables' in event else None
            if stageVariables is not None:
                env = stageVariables['Environment'] if 'Environment' in stageVariables else ""
            PED_Module.initiate(env)

            #log user and transaction details
            bodyCurtailed = Utility.curtailObject4Logging(body, "fileContentBase64")
            activityId = Utility.logUserActivity(bodyCurtailed, "generateQuizFromPDF")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            priorTranIds = body["priorTranIds"] if 'priorTranIds' in body else ""
            fileContent = body["fileContentBase64"] if 'fileContentBase64' in body else None
            fileName = body["fileName"] if 'fileName' in body else None
            questionCount = body["qestionCount"]  if "qestionCount" in body else None
            difficulty = body["difficulty"]  if "difficulty" in body else None
            questionType = body["questionType"]  if "questionType" in body else None
            explanation = body["explanation"]  if "explanation" in body else None
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
            
            if fileName is None or fileContent is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1002",
                        'error': 'Missing file name or file content in the request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # get the text from the file content
            inputValues = {
                            "fileContentBase64": fileContent,
                            "pdfFilename": fileName,
                            "userid": userid,
                            "tran_id": tran_id
                            }
            retVal = inputProcessor.storeInput("pdfContentBase64", \
                                                        **inputValues)
            if retVal is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'text could not be retrieved from provided document file',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # Create the local directory if it does not exist
            if retVal == "LOCAL_FILE_SAVE_FAILED":

                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'provided file content could not be saved locally',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            foldertoDelete = str(Path(retVal).parent)
            
            # # check for minimum length of the text- min 400 chars and max 35000 chars
            # if len(retVal) < 400:
                
            #     response = Utility.generateResponse(500, {
            #             'transactionId' : tran_id,
            #             'errorCode': "2003",
            #             'error': 'text is too short for any transformation',
            #             'AnswerRetrieved': False
            #         }, origin)
            #     Utility.updateUserActivity(str(activityId), userid, response)
            #     return response
            
            # if len(retVal) > 35000:
                
            #     response = Utility.generateResponse(500, {
            #             'transactionId' : tran_id,
            #             'errorCode': "2004",
            #             'error': 'text is too long for any transformation',
            #             'AnswerRetrieved': False
            #         }, origin)
            #     Utility.updateUserActivity(str(activityId), userid, response)
            #     return response

            # transform the input text 
            # newInst = instruction + " " + Utility.PROMPT_EXTENSION_4_HTML_OUTPUT \
            #     if instruction is not None else Utility.PROMPT_EXTENSION_4_HTML_OUTPUT
            inputs = {
                "questionCount" : questionCount,
                "difficulty" : difficulty,
                "questionTypes" : questionType,
                "explanation" : explanation,
                # "instruction": newInst
            }
            trmsJSON = transformationHandler.transformTextForQuizGenerationWithContext \
                                        (Path(retVal).parent, **inputs)

            if trmsJSON is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2004",
                        'error': 'model response could not be obtained',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            if trmsJSON == "PROMPT_NOT_GENERATED":
                
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2005",
                        'error': 'prompt could not be retrieved',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # save json in ppt 
            # upload the ppt to S3 and generate pre-signed URL
            localDocFileLocation = str(Path(Utility.EFS_LOCATION, userid))
            datetimestring = datetime.now().replace(tzinfo=timezone.utc).strftime("%m%d%Y%H%M%S")
            datetimeFormattedString = datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
            localDocFileName = "Quiz_"+ tran_id + "_" + datetimestring + ".qzx"
            localDocFilePath = str(Path(localDocFileLocation, localDocFileName))
            s3filePath = "/" + userid + "/" + localDocFileName
            presignedURL = outputGenerator.storeOutputFile(trmsJSON, "QUIZ", "JSON", \
                                                           localDocFileName, localDocFileLocation,\
                                                            s3filePath)
            
            if presignedURL is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2006",
                                    'error': 'quiz could not be stored',
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
                "fileType": "qzx",
                "fileStatus": "complete",
                "user-fileName": "",
            })

            if retVal is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2007",
                                    'error': 'document record could not be updated in database',
                                }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            


            # Return the response in JSON format
            response = Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': trmsJSON,
                                    'QuizFileId': retVal,
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                                   message=f"Error in generateQuizFromPDF Function: {str(e)}"))
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
        
        finally:
            deleteDirWithFiles(foldertoDelete)




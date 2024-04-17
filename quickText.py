import logging
import json, uuid
from common.lambdaFunction import invokeLambdaFunction
from datetime import datetime, timezone
from pathlib import Path
from common.prompts import Prompt
from common.globals import Utility, PED_Module
from common.essayModel import generateShortEssayWithMultipleInvokes, \
                        generateMediumEssayWithMultipleInvokes, generateLargeEssayWithMultipleInvokes

############################################################
############################################################
#return error codes:
# 1001 - missing user id in the request
# 1002 - missing input in the request
# 2001 - prompt could not be retrieved
# 2002 - model response could not be generated
# 2003 - file could not be uploaded to s3
# 5001 - Method level error
############################################################
def generateQuickText(event, context):
     
    # print(event)
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

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "generateQuickText")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            system_role = "system" 
            sl_role = body["role"] if 'role' in body else None
            sl_question = body["topic"] if 'topic' in body else None
            essaySize = body['essaySize'] if 'essaySize' in body else None
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
            
            if sl_role is None or sl_question is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1002",
                        'error': 'Missing system role or topic in the request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
                

            # Construct the chat messages with roles
            prompt = Prompt.getPrompt(Utility.QUICK_TEXT_PROMPT_TYPE)
            if prompt is None:
                
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'prompt could not be retrieved',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            dict = {
                    "TOPIC": sl_question
            } 
            prompt = Prompt.processPrompts(prompt, dict)
            print(prompt + "\n\n")

            # Create the chat completion
            modelResponse = ''
            if essaySize == 'l': # large essay
                modelResponse = generateLargeEssayWithMultipleInvokes \
                            ("You are a seasonsed " + sl_role, prompt, 'html', 'gpt-3.5-turbo', 3000, 2)
            elif essaySize == 'm': # medium essay 
                modelResponse = generateMediumEssayWithMultipleInvokes \
                            ("You are a seasonsed " + sl_role, prompt, 'html', 'gpt-3.5-turbo', 3000, 2)
            else:
                modelResponse = generateShortEssayWithMultipleInvokes \
                            ("You are a seasonsed " + sl_role, prompt, 'html', 'gpt-3.5-turbo', 3000, 2)
            
            if modelResponse is None or modelResponse == '':
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'model response could not be generated',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # save text in doc and upload to s3
            localFileLocation = str(Path(Utility.EFS_LOCATION, userid))
            datetimestring = datetime.now().replace(tzinfo=timezone.utc).strftime("%m%d%Y%H%M%S")
            datetimeFormattedString = datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
            localFileName = "DocumentFile_"+ tran_id + "_" + datetimestring + ".docx"
            localFilePath = str(Path(localFileLocation, localFileName))
            #print('localFilePath: ' + localFilePath)
            
            # upload the document in s3
            s3filePath = "/" + Utility.S3OBJECT_NAME_FOR_USER_FILES + "/" + localFileName
            presignedURL = Utility.uploadDocumentinTexttoS3(modelResponse, localFileName, \
                                                            localFileLocation, s3filePath)
            
            if presignedURL is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2003",
                        'error': 'File content could not be uploaded in s3',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # generate the sfdt format by invoking lambda function
            # DOES NOT WORK IF USED LOCALLY
            # payload = invokeLambdaFunction(Utility.DOC2SFDT_LAMBDA_FUNCTION_NAME,\
            #                             json.dumps({
            #                                 "filePath": localFilePath
            #                             }))
            
            # if 'sfdt' in payload and payload['sfdt'] != "":
            #     sfdt = payload['sfdt']
            # else:
            #     sfdt = ""

            # delete the local files and folders
            Path(localFilePath).unlink()
            localFolder = Path(localFileLocation)
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
                                                   f"Error in generateQuickText Function: {str(e)}"))
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
            

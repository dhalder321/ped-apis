import logging
import json, uuid
from common.globals import Utility, PED_Module
from transform.inputProcessor import inputProcessor 


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
def verifyDocument(event, context):

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
            env = ''
            stageVariables = event['stageVariables'] if 'stageVariables' in event else None
            if stageVariables is not None:
                env = stageVariables['Environment'] if 'Environment' in stageVariables else ""
            PED_Module.initiate(env)

            #log user and transaction details
            bodyCurtailed = Utility.curtailObject4Logging(body, "fileContentBase64")
            activityId = Utility.logUserActivity(body, "verifyDocument")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            fileContent = body["fileContentBase64"] if 'fileContentBase64' in body else None
            fileName = body["fileName"] if 'fileName' in body else None
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

            # get the text from the ppt content
            inputValues = {
                            "fileContentBase64": fileContent,
                            "docFilename": fileName,
                            "userid": userid,
                            "tran_id": tran_id
                            }
            retVal = inputProcessor.processInput("docContentBase64", \
                                                        **inputValues)
            
            # get the text from ppt file
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
            
            # check for minimum length of the text- min 400 chars and no max check
            if len(retVal) < 400:
                
                response = Utility.generateResponse(200, {
                        'transactionId' : tran_id,
                        'errorCode': "2003",
                        'Response': 'failure',
                        'errors': ['Text is too short for any transformation. Please add larger file that is less than 1 MB in size'],
                        'AnswerRetrieved': True
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # if len(retVal) > 35000:
            #     response = Utility.generateResponse(500, {
            #             'transactionId' : tran_id,
            #             'errorCode': "2004",
            #             'error': 'text is too long for any transformation',
            #             'AnswerRetrieved': False
            #         }, origin)
            #     Utility.updateUserActivity(str(activityId), userid, response)
            #     return response

            # Return the response in JSON format
            response = Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': 'success',
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                        f"Error in verifyDocument Function: {str(e)}"))
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                                   "Stack Trace:", exc_info=True))
            
            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "5001",
                                    'error': 'Error processing your request',
                                    'AnswerRetrieved': False
                                }, origin)
            Utility.updateUserActivity(str(activityId), -1, response)
            return response

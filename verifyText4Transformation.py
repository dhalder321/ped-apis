import logging
import json, uuid
from common.globals import Utility, PED_Module

############################################################
############################################################
#return error codes:
#  999 - No request object found
# 1001 - missing user id in the request
# 1002 - missing input in the request
# 2001 - text could not be retrieved from provided  file
# 2002 - model response could not be obtained
# 5001 - Method level error
############################################################
def verifyText(event, context):

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
            activityId = Utility.logUserActivity(body, "verifyText")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            text = body["text"] if 'text' in body else None
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
            
            if text is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1002",
                        'error': 'Missing text or rendering type in the request',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # check for minimum length of the text- min 400 chars or max 35000
            if len(text) < 400:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'text is too short for any transformation',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            if len(text) > 35000:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'text is too large for any transformation',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # Return the response in JSON format
            response = Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': "success",
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                                   f"Error in verifyText Function: {str(e)}"))
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

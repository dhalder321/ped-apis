import logging
import json, uuid
from common.prompts import Prompt
from common.globals import Utility, PED_Module
from common.essayModel import generateShortEssayWithMultipleInvokes

############################################################
############################################################
#return error codes:
# 1001 - missing user id in the request
# 1002 - missing input in the request
# 1003 - prompt could not be retrieved
# 5001 - Method level error
############################################################
def generateTextOfTopicOutline(event, context):
     
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

            #log user and transaction details
            activityId = Utility.logUserActivity(body, "generateTextOfTopicOutline")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            system_role = "system" 
            sl_role = body["role"] if 'role' in body else None
            sl_question = body["topic"] if 'topic' in body else None
            sl_summary = body["summary"] if 'summary' in body else None
            sl_outline = body['outline'] if 'outline' in body else None
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
            prompt = Prompt.getPrompt(Utility.TEXTOFTOPICOUTLINE_PROMPT_TYPE)
            if prompt is None:
                # Return a 400 Bad Request response if input is missing
                response = Utility.generateResponse(400, {
                        'transactionId' : tran_id,
                        'errorCode': "1003",
                        'error': 'prompt could not be retrieved',
                        'AnswerRetrieved': False
                    }, origin)
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            dict = {
                    "TOPIC": sl_question
            } 
            if sl_summary is not None:
                dict['SUMMARY'] = sl_summary
            else:
                dict['SUMMARY'] = ""
            
            if sl_outline is not None:
                dict['OUTLINE'] = sl_outline
            else:
                dict['OUTLINE'] = ""

            prompt = Prompt.processPrompts(prompt, dict)
            #print(prompt)

            # Create the chat completion
            modelResponse = generateShortEssayWithMultipleInvokes \
                            ("You are a seasonsed " + sl_role, prompt, 'html', 'gpt-3.5-turbo', 3000, 2)

            # Return the response in JSON format
            response = Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': modelResponse,
                                    'AnswerRetrieved': True
                                }, origin)
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in generateTextOfTopicOutline Function: {str(e)}")
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
            

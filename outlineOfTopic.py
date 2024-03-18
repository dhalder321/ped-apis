import logging
import json, uuid
from common.prompts import Prompt
from common.globals import Utility
from common.model import getModelResponse

############################################################
############################################################
#return error codes:
# 1001 - missing input in the request
# 5001 - Method level error
############################################################
def generateOutlineFromTopic(event, context):
     
    body = json.loads(event['body'])
    try:
        tran_id = body["transactionId"]
        if tran_id is None:
            tran_id = str(uuid.uuid1())
    
        # Parse the incoming JSON payload
        system_role = "system" 
        sl_role = body["role"]  
        sl_question = body["topic"]  
        sl_summary = body["summary"]  
        
        if sl_role is None or sl_question is None:
            # Return a 400 Bad Request response if input is missing
            return Utility.generateResponse(400, {
                    'transactionId' : tran_id,
                    'errorCode': "1001",
                    'error': 'Missing system role or topic in the request',
                    'AnswerRetrieved': False
                })
            

        # Construct the chat messages with roles
        prompt = Prompt.getPrompt(Utility.TEXT2TOPICOUTLINE_PROMPT_TYPE)
        dict = {
                "TOPIC": sl_question
        } 
        if sl_summary is not None:
            dict['SUMMARY'] = sl_summary
        else:
            dict['SUMMARY'] = ""

        prompt = Prompt.processPrompts(prompt, dict)
        
        # Create the chat completion
        modelResponse = getModelResponse("You are a seasonsed " + sl_role, \
                         prompt)

        # Return the response in JSON format
        return Utility.generateResponse(200, {
                                'transactionId' : tran_id,
                                'Response': modelResponse,
                                'AnswerRetrieved': True
                            })

    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in generateOutlineFromTopic Function: {str(e)}")
        logging.error("Stack Trace:", exc_info=True)
        
        # Return a 500 server error response
        return Utility.generateResponse(500, {
                                'transactionId' : tran_id,
                                'errorCode': "5001",
                                'error': 'Error processing your request',
                                'AnswerRetrieved': False
                            })
        

import json
import logging

class Utility:
  
  TOPIC2SUMMARY_PROMPT_TYPE = 'TOPIC2SUMMARY'
  TEXT2TOPICOUTLINE_PROMPT_TYPE = 'TEXT2TOPICOUTLINE'
  TEXTOFTOPICOUTLINE_PROMPT_TYPE = 'TEXTOFTOPICOUTLINE'

  EFS_LOCATION = 'C:\openai-sdk\ped-apis'

  ##################################################
  #Common terms in the prompts to replace 
  ###

  # System role: {{SYSTEM_ROLE}}
  # Topic: {{TOPIC}}
  # Summary: {{SUMMARY}}
  # Outline: {{OUTLINE}}
  
  ##################################################

  PROMPT_TYPE2FILE_NAME = {
    TOPIC2SUMMARY_PROMPT_TYPE: "TOPIC2SUMMARY.txt",
    TEXT2TOPICOUTLINE_PROMPT_TYPE: "TEXT2TOPICOUTLINE.txt",
    TEXTOFTOPICOUTLINE_PROMPT_TYPE: 'TEXTOFTOPICOUTLINE.txt'
  }

  ENVIRONMENT = "dev"

  @staticmethod
  def generateResponse(responseCode, bodyJson, headers=None):
      
      try:
      
        if headers is None:
            headers= {}

        headers['Content-Type'] = 'application/json'
        headers['Access-Control-Allow-Origin'] = '*'

        return {
                    'statusCode': responseCode,
                    'body': json.dumps(bodyJson),
                    'headers': headers
                }
      except Exception as e:
        logging.error(e)
        return None
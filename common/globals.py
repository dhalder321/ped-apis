import json
import logging
from html.parser import HTMLParser
from docx import Document
from common.db import DBManager

class Utility:
  
  TOPIC2SUMMARY_PROMPT_TYPE = 'TOPIC2SUMMARY'
  TEXT2TOPICOUTLINE_PROMPT_TYPE = 'TEXT2TOPICOUTLINE'
  TEXTOFTOPICOUTLINE_PROMPT_TYPE = 'TEXTOFTOPICOUTLINE'

  EFS_LOCATION = 'C:\openai-sdk\ped-apis'
  ENVIRONMENT = "dev"
  S3BUCKE_NAME = 'pedbuc'
  S3OBJECT_NAME_FOR_USER_FILES = 'user-files'

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
      
  @staticmethod
  def logUserActivity(body, methodName):

    user_id = body['userid'] if 'userid' in body else None
    tran_id_ = body['transactionId'] if 'transactionId' in body else None
    requestTime = body['requesttimeinUTC'] if 'requesttimeinUTC' in body else ""
    
    if user_id is None or tran_id_ is None:
      raise ValueError("User id or transactionid not sent in request")   
    
    if not user_id.isdigit():
       raise ValueError("User id sent in request is not a valid integer")

    DBManager.addRecordInDynamoTable("ped-useractivity", {
        "userid": int(user_id),
        "transactionid": tran_id_,
        "requestTimeInUTC": requestTime,
        "methodName": methodName,
        "requestBody": json.dumps(body)
      })
  

class HTML2Document(HTMLParser):
      
  def __init__(self, doc):
      super().__init__()
      self.doc = doc
      
  def handle_data(self, data):
      self.doc.add_paragraph(data)


import json
import logging
from html.parser import HTMLParser
from common.db import DBManager
from datetime import datetime, timezone

class Utility:
  
  TOPIC2SUMMARY_PROMPT_TYPE = 'TOPIC2SUMMARY'
  TEXT2TOPICOUTLINE_PROMPT_TYPE = 'TEXT2TOPICOUTLINE'
  TEXTOFTOPICOUTLINE_PROMPT_TYPE = 'TEXTOFTOPICOUTLINE'

  EFS_LOCATION = 'C:\openai-sdk\ped-apis'
  ENVIRONMENT = "dev"
  S3BUCKE_NAME = 'pedbuc'
  S3OBJECT_NAME_FOR_USER_FILES = 'user-files'


  ###################################################
  #              TABLE NAMES
  ####################################################
  #Environment: dev
  #Table names:
  USER_TABLE_NAME="ped-users"
  USERFILES_TABLE_NAME = "ped-userfiles" 
  USERACTIVITY_TABLE_NAME = "ped-useractivity" 

  #Environment: test
  #Table names:
  TEST_USER_TABLE_NAME="ped-users-test"
  TEST_USERFILES_TABLE_NAME = "ped-userfiles-test" 
  TEST_USERACTIVITY_TABLE_NAME = "ped-useractivity-test"

  #Environment: prod
  #Table names:
  PROD_USER_TABLE_NAME="ped-users-prod"
  PROD_USERFILES_TABLE_NAME = "ped-userfiles-prod" 
  PROD_USERACTIVITY_TABLE_NAME = "ped-useractivity-prod"

  ######################################################

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
    
    if user_id is None and methodName not in ("signupNewUser", "loginUser"):
      raise ValueError("userid not sent in request")
    elif user_id is None and methodName in ("signupNewUser", "loginUserWithemail", "loginUserWithKey"):
      user_id = "-1"
    else:
      if not user_id.isdigit():
        raise ValueError("User id sent in request is not a valid integer")

    if tran_id_ is None:
      raise ValueError("transactionid not sent in request")   
    
    return DBManager.addRecordInDynamoTableWithAutoIncrKey(DBTables.UserActivity_Table_Name, \
                                                    "staticIndexColumn", "activityid", \
                                                    "staticIndexColumn-activityid-index", \
                                                     {
                                                        "userid": int(user_id),
                                                        "transactionid": tran_id_,
                                                        "staticIndexColumn": 99,
                                                        "requestTimeInUTC": requestTime,
                                                        "apiMethodName": methodName,
                                                        "activityType": "APIInvoke",
                                                        "requestBody": json.dumps(body)
                                                      })
  
  @staticmethod
  def updateUserActivity(activityId, userid, response):
     if activityId is None or userid is None:
        return None
     
     return DBManager.updateRecordInDynamoTable(DBTables.UserActivity_Table_Name, \
                                              "activityid", activityId, \
                                              "userid", userid, \
                                                     {
                                                        "responseTimeInUTC": datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S"),
                                                        "responseStatus": "success" if response['statusCode'] == 200 else "failure", 
                                                        "responseBody": json.dumps(response)
                                                      })
  

class PED_Module:
   
   @staticmethod
   def initiate():
      DBTables.GetTableName()

class DBTables:
   User_Table_Name = ""
   UserFiles_Table_Name = ""
   UserActivity_Table_Name = ""

   @staticmethod
   def GetTableName():
      
      if Utility.ENVIRONMENT == "dev":
        DBTables.User_Table_Name = Utility.USER_TABLE_NAME   
        DBTables.UserFiles_Table_Name = Utility.USERFILES_TABLE_NAME   
        DBTables.UserActivity_Table_Name = Utility.USERACTIVITY_TABLE_NAME
      else:
        if Utility.ENVIRONMENT == "test":
          DBTables.User_Table_Name = Utility.TEST_USER_TABLE_NAME   
          DBTables.UserFiles_Table_Name = Utility.TEST_USERFILES_TABLE_NAME   
          DBTables.UserActivity_Table_Name = Utility.TEST_USERACTIVITY_TABLE_NAME
        else:
          DBTables.User_Table_Name = Utility.PROD_USER_TABLE_NAME   
          DBTables.UserFiles_Table_Name = Utility.PROD_USERFILES_TABLE_NAME   
          DBTables.UserActivity_Table_Name = Utility.PROD_USERACTIVITY_TABLE_NAME 
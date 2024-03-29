import json, os
import base64
import logging
from pathlib import Path
from html.parser import HTMLParser
from common.db import DBManager
from datetime import datetime, timezone
from docx import Document
from htmldocx import HtmlToDocx
from common.s3File import uploadFile 


class Utility:
  

  ##################################################
  #Common terms in the prompts to replace 
  ###

  # System role: {{SYSTEM_ROLE}}
  # Topic: {{TOPIC}}
  # Summary: {{SUMMARY}}
  # Outline: {{OUTLINE}}
  
  ##################################################

  TOPIC2SUMMARY_PROMPT_TYPE = 'TOPIC2SUMMARY'
  TEXT2TOPICOUTLINE_PROMPT_TYPE = 'TEXT2TOPICOUTLINE'
  TEXTOFTOPICOUTLINE_PROMPT_TYPE = 'TEXTOFTOPICOUTLINE'

  ESSAY_MODEL_OVERRIDE_PROMPT_TYPE = "ESSAY_MODEL_OVERRIDE_PROMPT"                         
  ESSAY_MODEL_SUBHEADING_PROMPT_TYPE = "ESSAY_MODEL_SUBHEADING_PROMPT"                        
  MEDIUM_ESSAY_MODEL_OVERRIDE_PROMPT_TYPE =  "MEDIUM_ESSAY_MODEL_OVERRIDE_PROMPT"                 
  MEDIUM_ESSAY_MODEL_SUBHEADING_PROMPT_TYPE =  "MEDIUM_ESSAY_MODEL_SUBHEADING_PROMPT"               
  SHORT_ESSAY_MODEL_OVERRIDE_PROMPT_TYPE =  "SHORT_ESSAY_MODEL_OVERRIDE_PROMPT"                  
  SHORT_ESSAY_MODEL_SUBHEADING_PROMPT_TYPE =  "SHORT_ESSAY_MODEL_SUBHEADING_PROMPT"               

  TRANSFORM_ANNOTATED_BIBLIOGRAPHY_PROMPT_TYPE =  "TRANSFORM_ANNOTATED_BIBLIOGRAPHY"         
  TRANSFORM_CRITICAL_RESPONSE_ESSAY_PROMPT_TYPE =  "TRANSFORM_CRITICAL_RESPONSE_ESSAY"        
  TRANSFORM_CRITICAL_RESPONSE_ESSAY_INSTRUCTION_PROMPT_TYPE =   "TRANSFORM_CRITICAL_RESPONSE_ESSAY_INSTRUCTION"                                        
  TRANSFORM_ESSAY_EXPANSION_ASSIGNMENT_PROMPT_TYPE =    "TRANSFORM_ESSAY_EXPANSION_ASSIGNMENT"   
  TRANSFORM_REFLECTION_PAPER_PROMPT_TYPE =    "TRANSFORM_REFLECTION_PAPER"             
  TRANSFORM_REFLECTION_PAPER_INSTRUCTION_PROMPT_TYPE =  "TRANSFORM_REFLECTION_PAPER_INSTRUCTION"   
  TRANSFORM_RESEARCH_PROPOSALS_PROMPT_TYPE =   "TRANSFORM_RESEARCH_PROPOSALS"            
  TRANSFORM_SEMINAR_DISCUSSION_POINTS_PROMPT_TYPE =  "TRANSFORM_SEMINAR_DISCUSSION_POINTS"      
  TRANSFORM_STUDY_GUIDE_PROMPT_TYPE =   "TRANSFORM_STUDY_GUIDE"    

  PROMPT_TYPE2FILE_NAME = {
         TOPIC2SUMMARY_PROMPT_TYPE: "TOPIC2SUMMARY.txt",
    TEXT2TOPICOUTLINE_PROMPT_TYPE: "TEXT2TOPICOUTLINE.txt",
    TEXTOFTOPICOUTLINE_PROMPT_TYPE: "TEXTOFTOPICOUTLINE.txt",

    ESSAY_MODEL_OVERRIDE_PROMPT_TYPE  :  "ESSAY_MODEL_OVERRIDE_PROMPT.txt",                         
    ESSAY_MODEL_SUBHEADING_PROMPT_TYPE  :  "ESSAY_MODEL_SUBHEADING_PROMPT.txt",                        
    MEDIUM_ESSAY_MODEL_OVERRIDE_PROMPT_TYPE  :   "MEDIUM_ESSAY_MODEL_OVERRIDE_PROMPT.txt",                 
    MEDIUM_ESSAY_MODEL_SUBHEADING_PROMPT_TYPE  :   "MEDIUM_ESSAY_MODEL_SUBHEADING_PROMPT.txt",               
    SHORT_ESSAY_MODEL_OVERRIDE_PROMPT_TYPE  :   "SHORT_ESSAY_MODEL_OVERRIDE_PROMPT.txt",                  
    SHORT_ESSAY_MODEL_SUBHEADING_PROMPT_TYPE  :   "SHORT_ESSAY_MODEL_SUBHEADING_PROMPT.txt",  
    
    TRANSFORM_ANNOTATED_BIBLIOGRAPHY_PROMPT_TYPE  :   "TRANSFORM_ANNOTATED_BIBLIOGRAPHY.txt",        
    TRANSFORM_CRITICAL_RESPONSE_ESSAY_PROMPT_TYPE  :   "TRANSFORM_CRITICAL_RESPONSE_ESSAY.txt",       
    TRANSFORM_CRITICAL_RESPONSE_ESSAY_INSTRUCTION_PROMPT_TYPE  :    "TRANSFORM_CRITICAL_RESPONSE_ESSAY_INSTRUCTION.txt",                                       
    TRANSFORM_ESSAY_EXPANSION_ASSIGNMENT_PROMPT_TYPE  :     "TRANSFORM_ESSAY_EXPANSION_ASSIGNMENT.txt",  
    TRANSFORM_REFLECTION_PAPER_PROMPT_TYPE  :     "TRANSFORM_REFLECTION_PAPER.txt",            
    TRANSFORM_REFLECTION_PAPER_INSTRUCTION_PROMPT_TYPE  :   "TRANSFORM_REFLECTION_PAPER_INSTRUCTION.txt",  
    TRANSFORM_RESEARCH_PROPOSALS_PROMPT_TYPE  :    "TRANSFORM_RESEARCH_PROPOSALS.txt",           
    TRANSFORM_SEMINAR_DISCUSSION_POINTS_PROMPT_TYPE  :   "TRANSFORM_SEMINAR_DISCUSSION_POINTS.txt",     
    TRANSFORM_STUDY_GUIDE_PROMPT_TYPE  :    "TRANSFORM_STUDY_GUIDE.txt",              
  }

  # Local_Location = 'C:\openai-sdk\ped-apis'
  Local_Location = './'
  Efs_Path = '/mnt/ped'
  EFS_LOCATION = Local_Location

  S3BUCKE_NAME = 'pedbuc'
  S3OBJECT_NAME_FOR_USER_FILES = 'user-files'
  S3OBJECT_NAME_FOR_PROMPT_FILES = 'prompts'

  TRASFORMATION_USER_ROLE = "You are a seasoned and experienced academician"
  PROMPT_EXTENSION_4_HTML_OUTPUT = "Generate the output strictly and strictly in HTML format with at minimum doctype, html, head and body tags and other basic HTML tags. Do NOT add any meta tags."

  ###################################################
  #              Environment variables
  ####################################################
  ENVIRONMENT = "dev"
  PROMPT_LOCATION = "local"  # or s3

  # CORS allowed origin
  CORS_ALLOWED_ORIGIN = "http://localhost:3000" 

  ###################################################


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

  @staticmethod
  def initiate():
    #if Utility.PROMPT_LOCATION != 'dev':
    Utility.EFS_LOCATION = Utility.Local_Location


  @staticmethod
  def generateResponse(responseCode, bodyJson, headers=None):
      
      try:
      
        if headers is None:
            headers= {}

        headers['Content-Type'] = 'application/json'
        #add CORS headers
        headers['Access-Control-Allow-Headers'] = 'Content-Type'
        headers['Access-Control-Allow-Origin'] = Utility.CORS_ALLOWED_ORIGIN
        headers['Access-Control-Allow-Methods'] = 'OPTIONS,POST,GET'

        return {
                    'statusCode': responseCode,
                    'body': json.dumps(bodyJson),
                    'headers': headers
                }
      except Exception as e:
        logging.error(e)
        return None
  
  @staticmethod
  def saveBase64FileInLocal(filePath, fileContentBase64):
    try:

      # check if folder exists, create it if not present
      path = Path(filePath)
      fileLocation = str(path.parent)
      isExist = os.path.exists(fileLocation)
      if not isExist:    
          os.makedirs(fileLocation)  

      #write the file
      with open(filePath,"wb") as f:
            f.write(base64.b64decode(fileContentBase64.encode("utf-8")))
      return True
    
    except Exception as e:
      logging.error(e)
      return False

  @staticmethod
  def uploadDocumentinHTMLtoS3(htmlContent, fileName, localFileLocation, s3FfilePath):

    #check for valid filename and file location
    if fileName is None or localFileLocation is None:
      return None
       
    #check for file location existance
    isExist = os.path.exists(localFileLocation)
    if not isExist:    
      os.makedirs(localFileLocation)

    localFilePath = str(Path(localFileLocation, fileName))

    document = Document()
    parser =  HtmlToDocx()
    parser.add_html_to_document(htmlContent, document)
    document.save(localFilePath)

    #upload to S3
    s3fileLocation = Utility.S3OBJECT_NAME_FOR_USER_FILES + "/" + Utility.ENVIRONMENT
    s3filePath = s3fileLocation + s3FfilePath
    print("s3filePath:" + s3filePath)
    presignedURL = uploadFile(localFilePath, Utility.S3BUCKE_NAME, s3filePath)
    
    return presignedURL
      
  @staticmethod
  def logUserActivity(body, methodName):

    user_id = body['userid'] if 'userid' in body else None
    tran_id_ = body['transactionId'] if 'transactionId' in body else None
    requestTime = body['requesttimeinUTC'] if 'requesttimeinUTC' in body else ""
    
    if user_id is None and methodName not in ("signupNewUser", "loginUserWithemail", "loginUserWithAccessKey"):
      raise ValueError("userid not sent in request")
    elif user_id is None and methodName in ("signupNewUser", "loginUserWithemail", "loginUserWithAccessKey"):
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
      Utility.initiate()

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
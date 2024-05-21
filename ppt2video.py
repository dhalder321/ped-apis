import logging
import json, uuid
from pathlib import Path 
from datetime import datetime, timezone
from common.db import DBManager
from common.globals import Utility, PED_Module, DBTables
from common.s3File import upload_file, uploadDirInRecursive, getFileDirectories, downloadDirectory
from transform.inputProcessor import inputProcessor
from transform.outputGenerator import outputGenerator 
from common.voiceOver import generateVoiceOverFiles 
from common.video import generateVideo
from ppt2image import getImagesFromPPT
from common.lambdaFunction import invokeLambdaFunction


############################################################
############################################################
#return error codes:
#  999 - No request object found
# 1001 - missing user id in the request
# 1002 - missing input in the request
# 2001 - text could not be retrieved from provided presentation file
# 2002 - provided file content could not be saved locally
# 2003 - text is too short for any transformation
# 2004 - model response could not be obtained
# 2005 - prompt could not be retrieved
# 2006 - document could not be stored
# 2007 - document record could not be updated in database
# 5001 - Method level error
############################################################
def generateVideoFromPresentation(event, context):

    # print(event)
    logging.debug(event)

    #process OPTIONS method
    if 'httpMethod' in event and event['httpMethod'] == 'OPTIONS':
      return Utility.generateResponse(200, {})


    #process only POST methods
    if 'httpMethod' in event and event['httpMethod'] == 'POST':

        if 'body' not in event or event['body'] is None:
            return Utility.generateResponse(400, {
                        'errorCode': "999",
                        'error': 'No request object found',
                    })
        
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
            activityId = Utility.logUserActivity(bodyCurtailed, "generateVideoFromPresentation")

            tran_id = body["transactionId"]
            if tran_id is None:
                tran_id = str(uuid.uuid1())
        
            # Parse the incoming JSON payload
            priorTranIds = body["priorTranIds"] if 'priorTranIds' in body else ""
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
                    })
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
                    })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response

            # STEP 1: generate audio script files
            # check the slide notes and save them in text files
            inputValues = {
                            "fileContentBase64": fileContent,
                            "pptFilename": fileName,
                            "userid": userid,
                            "tran_id": tran_id
                            }
            pptFilePath = inputProcessor.processPPTInput4Video(**inputValues)
            
            # get the text from ppt file
            if pptFilePath is None:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2001",
                        'error': 'text could not be retrieved from provided presentation file',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            if pptFilePath == "LOCAL_FILE_SAVE_FAILED":

                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2002",
                        'error': 'provided file content could not be saved locally',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            if pptFilePath == "AUDIO_SCRIPT_GENERATTION_FAILED":
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2003",
                        'error': 'audio scripts could not be generated',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            workingDir = Path(pptFilePath).parent
            scriptFilePath = str(Path(workingDir, "script"))
            print("***************Script files generated successfully**************************")

            
            # STEP 2: Invoke Windows API for Image conversion
            # invoke the lambda function to get the images created
            # pass the local ppt file path
            # retVal = invokeLambdaFunction(Utility.PPT_2_IMAGE_GENERATION_API_URL, 
            #                                 {
            #                                     "pptFilePath": pptFilePath,
            #                                     })
            #Updload the ppt file in S3 /tmp folder
            if not upload_file(str(Path(pptFilePath).name), Utility.S3BUCKE_NAME, 
                               Utility.S3OBJECT_NAME_FOR_TEMPORARY_FILES + "/" + userid):
                logging.debug("File could not be uploaded in S3 for image conversion.")
                return None
            
            # s3ImgPath = InvokeRestAPIForImageConversion(Utility.S3OBJECT_NAME_FOR_TEMPORARY_FILES + "/" + userid, 
                                                    #   str(Path(pptFilePath).name))
            
            # download images into local image path


            # logging.debug("output from ppt2image lambda function:" + str(retVal))

            # check for image file path            
            imageFilePath = str(Path(Path(pptFilePath).parent, "images"))

            if imageFilePath is None or Path(imageFilePath).exists == False \
                            or not any(Path(imageFilePath).iterdir()) :
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2004",
                        'error': 'image files could not be generated',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            # print("***************image files generated successfully**************************")
            
            # STEP 3: generate the voice over
            audioFilePath = str(Path(Path(pptFilePath).parent, "audio"))
            retVal = generateVoiceOverFiles(scriptFilePath, audioFilePath)
            if retVal != audioFilePath:
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2005",
                        'error': 'audio files could not be generated',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            print("***************audio files generated successfully**************************")

            # STEP 4: generate the video
            backgroundMusicPath = Path(Utility.EFS_LOCATION, Utility.VIDEO_GENERATION_BACKGROUND_MUSIC_FILE_NAME)
            videoFilePath = generateVideo(imageFilePath, audioFilePath, \
                                          str(backgroundMusicPath), str(workingDir))
            
            if videoFilePath is None or videoFilePath == '':
                response = Utility.generateResponse(500, {
                        'transactionId' : tran_id,
                        'errorCode': "2006",
                        'error': 'video file could not be generated',
                        'AnswerRetrieved': False
                    })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            print("***************video file generated successfully**************************")

            # STEP 5: upload to S3 and return the link
            localVideoFileLocation = workingDir
            datetimestring = datetime.now().replace(tzinfo=timezone.utc).strftime("%m%d%Y%H%M%S")
            datetimeFormattedString = datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
            localVideoFileName = Path(videoFilePath).stem
            localVideoFilePath = str(Path(localVideoFileLocation, localVideoFileName))
            s3filePath = "/" + userid + "/" + localVideoFileName
            presignedURL = outputGenerator.storeVideoFile(localVideoFilePath, s3filePath)
            
            if presignedURL is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2007",
                                    'error': 'video could not be stored',
                                })
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
                "fileName": localVideoFileName,
                "s3Filelocation": s3filePath,
                "s3bucketName": Utility.S3BUCKE_NAME,
                "initials3PresignedURLGenerated": presignedURL,
                "fileCreationDateTime": datetimeFormattedString,
                "fileType": "video",
                "fileStatus": "complete",
                "user-fileName": "",
            })

            if retVal is None:
                # Return a 500 server error response
                response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "2008",
                                    'error': 'video record could not be updated in database',
                                })
                Utility.updateUserActivity(str(activityId), userid, response)
                return response
            
            # delete the local files and folders
            # try:
            #     shutil.rmtree(workingDir)
            # except Exception as e:
            #     print("working dir cleanup for video generation failed ::" + str(e))

            # Return the response in JSON format
            response = Utility.generateResponse(200, {
                                    'transactionId' : tran_id,
                                    'Response': presignedURL,
                                    'AnswerRetrieved': True
                                })
            Utility.updateUserActivity(str(activityId), userid, response)
            return response

        except Exception as e:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(Utility.formatLogMessage(tran_id, userid, \
                                                   message=f"Error in generateVideoFromPresentation Function: {str(e)}"))
            logging.error("Stack Trace:", exc_info=True)

            # Return a 500 server error response
            response = Utility.generateResponse(500, {
                                    'transactionId' : tran_id,
                                    'errorCode': "5001",
                                    'error': 'Error processing your request',
                                    'AnswerRetrieved': False
                                })
            Utility.updateUserActivity(str(activityId), -1, response)
            return response

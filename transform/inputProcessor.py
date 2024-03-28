import json, uuid
from pathlib import Path
from datetime import datetime, timezone
from common.db import DBManager
from docx import Document
from htmldocx import HtmlToDocx
from common.globals import Utility, PED_Module, DBTables
from common.pptfile import getTextFromPPTX

class inputProcessor:


    @staticmethod
    def processInput(inputType, **inputValue):

        # ppt content in base64 format
        # inputs required : fileContentBase64, pptFilename, userid, tran_id 
        if inputType == "pptContentBase64":
            #check the valid inputs provided
            if  'fileContentBase64' not in inputValue or \
                inputValue["fileContentBase64"] is None:

                return "INVALID_FILE_CONTENT"
            
            if  'pptFilename' not in inputValue or \
                inputValue["pptFilename"] is None:

                return "INVALID_FILE_NAME"
            
            if  'userid' not in inputValue or \
                inputValue["userid"] is None:

                return "INVALID_USER_ID"
            
            if  'tran_id' not in inputValue or \
                inputValue["tran_id"] is None:

                return "INVALID_TRAN_ID"
            
            #process the ppt file
            return inputProcessor.processPPTFileContentBase64(inputValue["fileContentBase64"], \
                    inputValue["pptFilename"], inputValue["userid"], inputValue["tran_id"])
            


    def processPPTFileContentBase64(fileContentBase64, pptFileName, userid, tran_id):
            
        # save the ppt file locally
        localFileLocation = str(Path(Utility.EFS_LOCATION, userid))
        datetimestring = datetime.now().replace(tzinfo=timezone.utc).strftime("%m%d%Y%H%M%S")
        # datetimeFormattedString = datetime.now().replace(tzinfo=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")
        localFileName = "Uploaded-PPT_"+ tran_id + "_" + datetimestring + ".pptx"
        localFilePath = str(Path(localFileLocation, localFileName))
        #print('localFilePath: ' + localFilePath)
        
        # Create the local directory if it does not exist
        if Utility.saveBase64FileInLocal(localFilePath, fileContentBase64) == False:
            return "LOCAL_FILE_SAVE_FAILED"
        
        # get the ppt text
        text = getTextFromPPTX(localFilePath)

        # delete the temp files and folders
        Path(localFilePath).unlink()
        localFolder = Path(localFileLocation)
        if localFolder is not None and not any(localFolder.iterdir()):
            localFolder.rmdir()

        return text
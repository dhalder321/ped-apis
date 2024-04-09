import logging
import os
import json, uuid
from pathlib import Path
from datetime import datetime, timezone
from docx import Document
from htmldocx import HtmlToDocx
from common.globals import Utility, PED_Module, DBTables
from common.s3File import uploadFile


class outputGenerator:


    @staticmethod
    def storeOutputFile(text, outputFormat, textType, fileName, localFileLocation, s3Path):

        if outputFormat == "DOC" and textType == "HTML":
            return Utility.uploadDocumentinHTMLtoS3(text, fileName, \
                                                localFileLocation, s3Path)
        
        elif outputFormat == 'PPT' and textType == 'JSON':
            return Utility.uploadPPTinJSONtoS3(text, fileName, \
                                                localFileLocation, s3Path)
        
        elif outputFormat == 'QUIZ' and textType == 'JSON':
            return Utility.uploadQuizinJSONtoS3(text, fileName, \
                                                localFileLocation, s3Path)
        
        

    @staticmethod
    def storeVideoFile(localVideoFilePath, s3filePath):

        #upload to S3
        s3fileLocation = Utility.S3OBJECT_NAME_FOR_USER_FILES + "/" + Utility.ENVIRONMENT
        s3file = s3fileLocation + s3filePath
        print("s3filePath:" + s3file)
        presignedURL = uploadFile(localVideoFilePath, Utility.S3BUCKE_NAME, s3file)
        
        return presignedURL
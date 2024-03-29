import logging
import os
import json, uuid
from pathlib import Path
from datetime import datetime, timezone
from docx import Document
from htmldocx import HtmlToDocx
from common.globals import Utility, PED_Module, DBTables


class outputGenerator:


    @staticmethod
    def storeOutputFile(text, outputFormat, textType, fileName, localFileLocation, s3Path):

        if outputFormat == "DOC" and textType == "HTML":
            return Utility.uploadDocumentinHTMLtoS3(text, fileName, \
                                                localFileLocation, s3Path)
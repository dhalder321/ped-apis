import json
import uuid
import logging
from pathlib import Path
from common.globals import Utility
from ppt2ImageResponseHandler import check_message_subject
from common.s3File import upload_file, getFileDirectories, downloadDirectory
from common.sqs import dropMessage

queue_url = Utility.PPT2IMAGE_REQUEST_Q_URL


def generateImagesFromS3PPT(pptLocalFilePath:str, s3Path, fileName):

    try:
        #Updload the ppt file in S3 /tmp folder
        if not upload_file(Utility.S3BUCKE_NAME, pptLocalFilePath, s3Path + "/" + fileName):
            # (str(Path(pptLocalFilePath).name), Utility.S3BUCKE_NAME, fileName, s3Path):
            logging.debug("File could not be uploaded in S3 for image conversion.")
            return "S3_FILE_UPLOAD_FAILED"
        
        # drop the message in SQS q
        msgID = str(uuid.uuid1())
        dropMessage(queue_url, {
            'MessageId': msgID,
            'Subject': msgID,
            's3DirPath': s3Path,
            'fileName': fileName
        }, 
        "ppt2Imagev1", 
        msgID)

        print("SQS message has been dropped. waiting for response...")
        # read for response in SQS response q &
        # download images into local image path
        if check_message_subject(msgID, 15, 55) == False:
            logging.error("Response of PPT to Image could not be retrieved")
            return "IMAGES_NOT_GENERATED"
        
        files, folders = getFileDirectories(Utility.S3BUCKE_NAME, s3Path + "/" + "images")
        imageLocalPath = downloadDirectory(Utility.S3BUCKE_NAME, str(Path(pptLocalFilePath).parent), 
                                           files, folders)

        return imageLocalPath

    except Exception as e:
        logging.error("error in generateImagesFromS3PPT method: " + str(e))

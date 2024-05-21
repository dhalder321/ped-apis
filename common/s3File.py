
import logging
import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
from genericpath import isfile

def downloadFile(targetFileName, bucket, object_name=None):

    if targetFileName is None:
        raise ClientError("Error in downloadFile method: target file name not provided.")

    try:
        s3 = boto3.client('s3')
        with open(targetFileName, 'wb') as f:
            s3.download_fileobj(bucket, object_name, f)
        
    except ClientError as e:
        logging.error(e)
        return None
    

def readFile(bucket, object_name=None):

    if bucket is None:
        raise ClientError("Error in readFile method: bucket name not provided.")

    try:
        s3 = boto3.client('s3')
        # Read an object from the bucket
        response = s3.get_object(Bucket=bucket, Key=object_name)
        if 'Body' in response:
            object_content = response['Body'].read().decode('utf-8')
            return object_content
        
        return None
    except ClientError as e:
        logging.error(e)
        return None

def readFileBinary(bucket, object_name=None):

    if bucket is None:
        raise ClientError("Error in readFile method: bucket name not provided.")

    try:
        s3 = boto3.client('s3')
        # Read an object from the bucket
        response = s3.get_object(Bucket=bucket, Key=object_name)
        if 'Body' in response:
            object_content = response['Body'].read()
            return object_content
        
        return None
    except ClientError as e:
        logging.error(e)
        return None


def uploadFile(file_name, bucket, object_name=None):
    
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: presigned URL if file was uploaded, else None
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        return createS3PresignedURL(bucket, object_name)
    
    except ClientError as e:
        logging.error(e)
        return None
    
def upload_file(bucketName, file_name, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucketName, object_name)
    except ClientError as e:
        print(e)
        return False
    return True

def uploadDirInRecursive(bucketName, localDir, awsInitDir, space=""):

    print(space+"Processing dir: "+localDir)
    for file in os.listdir(localDir):
        file_path = str(Path(localDir,file))
        if file != "logs":
            if isfile(file_path):
                upload_file(bucketName, file_path, awsInitDir+"/"+file)
            else:
                uploadDirInRecursive(bucketName, file_path, awsInitDir+"/"+file, space+"  ")
    print(space+"... Done")
    
def getFileDirectories(bucket_name, prefix=""):
    file_names = []
    folders = []

    default_kwargs = {
        "Bucket": bucket_name,
        # "Marker": s3path, 
        "Prefix": prefix
    }
    next_token = ""
    s3_client = boto3.client('s3')
    while next_token is not None:
        updated_kwargs = default_kwargs.copy()
        if next_token != "":
            updated_kwargs["ContinuationToken"] = next_token

        response = s3_client.list_objects_v2(**default_kwargs)
        contents = response.get("Contents")

        if contents is not None:
            keys = list(filter(lambda x: x.get("Key", '').startswith(prefix), contents))
            for result in keys:
                key = result.get("Key")
                if key[-1] == "/":
                    folders.append(key)
                else:
                    file_names.append(key)

        next_token = response.get("NextContinuationToken")

    return file_names, folders


def downloadDirectory(bucket_name, local_path, file_names, folders):

    local_path = Path(local_path)
    s3_client = boto3.client('s3')

    for folder in folders:
        folder_path = Path.joinpath(local_path, folder)
        folder_path.mkdir(parents=True, exist_ok=True)

    for file_name in file_names:
        file_path = Path.joinpath(local_path, file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        s3_client.download_file(
            bucket_name,
            file_name,
            str(file_path)
        )

def deleteFile(bucket, object_name=None):

    try:
        s3_client = boto3.client("s3")
        response = s3_client.delete_object(Bucket=bucket, Key=object_name)
    
    except ClientError as e:
        logging.error(e)
        return None
    

def createS3PresignedURL(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def copyS3toEphemeral(s3BucketName, object_name, targetPath, targetFileName):

    try:
        fileContent = readFile(s3BucketName, object_name)
        filePath = str(Path(targetPath, targetFileName))

        with open(filePath, 'w') as f:
            f.write(fileContent)
        return True
    
    except Exception as e:
        logging.error("Error copying file from s3 to target location: " + str(e))
        return False
    

def copyBinaryS3toEphemeral(s3BucketName, object_name, targetPath, targetFileName):

    try:
        fileContent = readFileBinary(s3BucketName, object_name)
        filePath = str(Path(targetPath, targetFileName))

        with open(filePath, 'wb') as f:
            f.write(fileContent)
        return True
    
    except Exception as e:
        logging.error("Error copying file from s3 to target location: " + str(e))
        return False
    

if __name__ == "__main__":
  copyBinaryS3toEphemeral("pedbuc", "BasicPresentationTextTemplate.pptx", "c:\\openai-sdk", 
                          "BasicPresentationTextTemplate.pptx")
  
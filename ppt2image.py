import win32com.client
import win32api
import pythoncom
import os, logging
from pathlib import Path
from common.s3File import downloadDirectory, getFileDirectories, uploadDirInRecursive
from common.file import deleteDirWithFiles

def getImagesFromS3PPT(s3Bucket, s3DirPath, targetDirPath, fileName):

    try:

        folderToDelete = ''

        file_names, folder_names = getFileDirectories(s3Bucket, s3DirPath + "/")

        localPath = downloadDirectory(s3Bucket, targetDirPath, file_names, folder_names, fileName)

        if localPath is None:
            print("local path is null")
        else:
            print ("local path: "+  str(localPath))

        print(str(Path(localPath, fileName)) + "\n")

        folderToDelete = localPath # Path(targetDirPath, Path(s3DirPath).parts[0])

        imgPath = getImagesFromPPT(str(Path(localPath, fileName)))

        if Path(imgPath).exists():
            uploadDirInRecursive(s3Bucket, str(localPath), s3DirPath)

        return imgPath

    except Exception as e:
        logging.error("Error in getImagesFromS3PPT method::" + str(e) )
        return None
    finally:
        deleteDirWithFiles(folderToDelete)        




def getImagesFromPPT(pptFilePath):

    print("1")
    # pythoncom.CoInitialize()
    print("2")

    # Create a PowerPoint application object
    Application = win32com.client.Dispatch("PowerPoint.Application")
    print("3")

    try:
        print(pptFilePath)

        # Open the presentation without making it visible
        Presentation = Application.Presentations.Open(pptFilePath, WithWindow=False)
        print("4")

        # Create a folder to save the slides as images
        imageFilePath = os.path.join(os.path.dirname(pptFilePath), "images")
        if not os.path.exists(imageFilePath):
            os.makedirs(imageFilePath)

        print("5")

        # Export each slide as an image
        for i, slide in enumerate(Presentation.Slides):
            image_path = os.path.join(imageFilePath, f"{i + 1}.png")
            slide.Export(image_path, "JPG")
        
        print("6")


        # Close the presentation
        Presentation.Close()

        print("7")

        return imageFilePath
    
    except Exception as e:
        print("An error occurred: " + str(e))
        print (win32api.FormatMessage(-2147352567))
        return None
    finally:
        # Quit the PowerPoint application
        Application.Quit()

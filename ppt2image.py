import win32com.client
import win32api
import os, logging
from pathlib import Path
from common.s3File import downloadDirectory, getFileDirectories, uploadDirInRecursive
from common.file import deleteDirWithFiles

def getImagesFromS3PPT(s3Bucket, s3DirPath, targetDirPath, fileName):

    try:

        folderToDelete = ''

        file_names, folders = getFileDirectories(s3Bucket, s3DirPath + "/")
        downloadDirectory(s3Bucket, targetDirPath, file_names, folders)

        folderToDelete = Path(targetDirPath, Path(s3DirPath).parts[0])

        imgPath = getImagesFromPPT(str(Path(targetDirPath, folders[0], fileName)))

        if Path(imgPath).exists():
            uploadDirInRecursive(s3Bucket, str(Path(targetDirPath, folders[0])), s3DirPath)
            

        return 
    except Exception as e:
        logging.error("Error in getImagesFromS3PPT method::" + str(e) )
        return None
    finally:
        deleteDirWithFiles(folderToDelete)        




def getImagesFromPPT(pptFilePath):

    # Create a PowerPoint application object
    Application = win32com.client.Dispatch("PowerPoint.Application")

    try:
        # Open the presentation without making it visible
        Presentation = Application.Presentations.Open(pptFilePath, WithWindow=False)

        # Create a folder to save the slides as images
        imageFilePath = os.path.join(os.path.dirname(pptFilePath), "images")
        if not os.path.exists(imageFilePath):
            os.makedirs(imageFilePath)

        # Export each slide as an image
        for i, slide in enumerate(Presentation.Slides):
            image_path = os.path.join(imageFilePath, f"{i + 1}.png")
            slide.Export(image_path, "JPG")
            

        # Close the presentation
        Presentation.Close()

        return imageFilePath
    
    except Exception as e:
        print("An error occurred: " + str(e))
        print (win32api.FormatMessage(-2147352567))
        return None
    finally:
        # Quit the PowerPoint application
        Application.Quit()

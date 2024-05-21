from common.globals import Utility
from fastapi import FastAPI
import uvicorn
from pathlib import Path
from ppt2image import getImagesFromS3PPT


app = FastAPI()


@app.post("/ppt2Image")
async def CreateImages(s3DirPath: str, 
                       fileName: str):

    imgPath = ''
    if s3DirPath is not None and s3DirPath != '':
        imgPath = getImagesFromS3PPT(Utility.S3BUCKE_NAME, s3DirPath, 
                                     Utility.WINDOWS_LOCAL_PATH, fileName)

    return imgPath




if __name__ == "__main__":
    uvicorn.run("fastAPIs:app", host="127.0.0.1", port=5000, log_level="info")
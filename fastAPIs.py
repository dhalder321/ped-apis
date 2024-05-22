from common.globals import Utility
from fastapi import FastAPI
from pydentic import BaseModel
import uvicorn
from pathlib import Path
from ppt2image import getImagesFromS3PPT


app = FastAPI()

class CreateImagesRequest(BaseModel):
    s3DirPath : str
    fileName: str

@app.post("/ppt2Image")
async def CreateImages(request: CreateImagesRequest):

    imgPath = ''
    if request.s3DirPath is not None and request.s3DirPath != '':
        imgPath = getImagesFromS3PPT(Utility.S3BUCKE_NAME, request.s3DirPath, 
                                     Utility.WINDOWS_LOCAL_PATH, request.fileName)

    return imgPath




if __name__ == "__main__":
    uvicorn.run("fastAPIs:app", host="0.0.0.0", port=5000, log_level="info")
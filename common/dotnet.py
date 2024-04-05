from pythonnet import load
load("coreclr")

import clr

clr.AddReference("C:\\openai-sdk\\ped-apis\\dlls\\ped-api-raw.dll")


from ped_api_raw import PPT2Images

def convertPPT2Images(pptFilePath):

    cls = PPT2Images()

    return cls.convertPPT2Image(pptFilePath)
import logging
from pathlib import Path
from common.globals import Utility

# s3BucketObjectName = 'prompts/'
efsLocation = Utility.EFS_LOCATION + '/prompts'

class Prompt:

    @staticmethod
    def getPromptsForSettings(settings):
        raise NotImplementedError()

    @staticmethod
    def getPrompt(promptType, env=None):

        # #environment name in the s3 object name
        # s3BucketObjectName += '/' + env

        #get the file name based on prompt type
        fileName = Utility.PROMPT_TYPE2FILE_NAME[promptType]
        fileName = Path(efsLocation, fileName)

        try:

            #read the file from EFS location and return the text
            data = Path(fileName).read_text()
            return data

        except Exception as e:
            logging.error(e)
            return None

    @staticmethod
    def processPrompts(prompt, dic):

        if prompt is None or dic is None:
            return prompt
        
        for k in dic.keys():
            prompt = prompt.replace("{{" + k+ "}}", dic[k])

        return prompt




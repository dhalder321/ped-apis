import logging
from pathlib import Path
from common.globals import Utility
from common.s3File import readFile

# s3BucketObjectName = 'prompts/'


class Prompt:

    @staticmethod
    def getPromptsForSettings(settings):
        raise NotImplementedError()

    @staticmethod
    def getPrompt(promptType, promp_location='s3', env=None):

        #get the file name based on prompt type
        fileName = Utility.PROMPT_TYPE2FILE_NAME[promptType]

        if promp_location == 's3':

            # #environment name in the s3 object name
            # s3BucketObjectName += '/' + env
            s3PromptLocation = Utility.S3OBJECT_NAME_FOR_PROMPT_FILES + "/" + Utility.ENVIRONMENT
            s3_object_name = s3PromptLocation + "/" + fileName

            return readFile(Utility.S3BUCKE_NAME, s3_object_name)

        elif promp_location == 'local':
            
            efsLocation = Utility.EFS_LOCATION + '/prompts'
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

    @staticmethod
    def getPromptAfterProcessing(promptType, dic, promp_location='local', env=None):

        prompt = Prompt.getPrompt(promptType, promp_location, env)

        if prompt is None:
            return prompt
        
        return Prompt.processPrompts(prompt, dic)



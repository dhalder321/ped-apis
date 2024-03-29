import os
import json, uuid
from datetime import datetime, timezone
from common.prompts import Prompt
from common.model import retryModelForOutputType
from common.essayModel import generateLargeEssayWithMultipleInvokes
from common.globals import Utility


class transformationHandler:

    @staticmethod
    def transformText(text, transformType, **inputValue):

        system_role = "system" 
        sl_role = Utility.TRASFORMATION_USER_ROLE

        if transformType == "Study guide":
            promptType = Utility.TRANSFORM_STUDY_GUIDE_PROMPT_TYPE
        elif transformType == "Seminar discussion":
            promptType = Utility.TRANSFORM_SEMINAR_DISCUSSION_POINTS_PROMPT_TYPE
            
        elif transformType == "Research proposals":
            promptType = Utility.TRANSFORM_RESEARCH_PROPOSALS_PROMPT_TYPE
            
        elif transformType == "Reflection paper":
            promptType = Utility.TRANSFORM_REFLECTION_PAPER_PROMPT_TYPE
            
        elif transformType == "Reflection paper instruction":
            promptType = Utility.TRANSFORM_REFLECTION_PAPER_INSTRUCTION_PROMPT_TYPE
        elif transformType == "Essay expansion assignment":
            promptType = Utility.TRANSFORM_ESSAY_EXPANSION_ASSIGNMENT_PROMPT_TYPE
            
        elif transformType == "Critical analysis":
            promptType = Utility.TRANSFORM_CRITICAL_RESPONSE_ESSAY_PROMPT_TYPE
        elif transformType == "Critical analysis instruction":
            promptType = Utility.TRANSFORM_CRITICAL_RESPONSE_ESSAY_INSTRUCTION_PROMPT_TYPE
        elif transformType == "Annotated bibliography":
            promptType = Utility.TRANSFORM_ANNOTATED_BIBLIOGRAPHY_PROMPT_TYPE
        
        #check for promptType
        if promptType is None:
            return "PROMPT_NOT_GENERATED"
            
        # construct the prompt from the provided input 
        prompt = Prompt.getPromptAfterProcessing(promptType, \
                                                 {
                                                    "TEXT": text,
                                                    "INSTRUCTION": inputValue["instruction"]
                                                    })
        if prompt is None:
            return "PROMPT_NOT_GENERATED"
        print(prompt)

        # transform the text as per prompt and generate it in html format
        return retryModelForOutputType(sl_role, \
                                prompt, 'html', 'gpt-3.5-turbo', 4096, 2)
            
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

    @staticmethod    
    def transformTextForPPTGeneration(text, **inputValue):
        system_role = "system" 
        sl_role = Utility.TRASFORMATION_USER_ROLE

        dic = {
            'TEXT': text,
            "CONTENT_INSTRUCTION" : '',
            "NOTES_INSTRUCTION": '',
            "SAMPLE_JSON": '',
            "SLIDE_COUNT": inputValue["slideCount"],
        }
        if inputValue["contentType"] == "Summary":
            promptType = Utility.TRANSFORM_PPT_SUMMARY_PROMPT_TYPE
            
        if inputValue["contentType"] == "Full Text":
            promptType = Utility.TRANSFORM_PPT_FULLTEXT_PROMPT_TYPE
        
        if inputValue["format"] == "Text only":
            dic["CONTENT_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_CONTENT_TEXTONLY_INSTRUCTION_PROMPT_TYPE)
            if inputValue["notes"] == 'y':
                dic["NOTES_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_NOTES_INSTRUCTION_PROMPT_TYPE)
                dic["SAMPLE_JSON"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_TEXT_NOTES_FORMAT_PROMPT_TYPE)
            elif inputValue['notes'] == 'n':
                dic["NOTES_INSTRUCTION"] = "\n DO NOT generate any notes for slides.\n"
                dic["SAMPLE_JSON"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_TEXT_FORMAT_PROMPT_TYPE)

        elif inputValue["format"] == "List with text":
            dic["CONTENT_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_CONTENT_LISTANDTEXTONLY_INSTRUCTION_PROMPT_TYPE)
            if inputValue["notes"] == 'y':
                dic["NOTES_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_NOTES_INSTRUCTION_PROMPT_TYPE)
                dic["SAMPLE_JSON"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDTEXT_NOTES_FORMAT_PROMPT_TYPE)
            elif inputValue['notes'] == 'n':
                dic["NOTES_INSTRUCTION"] = "\n DO NOT generate any notes for slides.\n"
                dic["SAMPLE_JSON"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDTEXT_FORMAT_PROMPT_TYPE)

        elif inputValue["format"] == "List with headings":
            dic["CONTENT_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_CONTENT_LISTANDHEADINGONLY_INSTRUCTION_PROMPT_TYPE)
            if inputValue["notes"] == 'y':
                dic["NOTES_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_NOTES_INSTRUCTION_PROMPT_TYPE)
                dic["SAMPLE_JSON"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDHEADING_NOTES_FORMAT_PROMPT_TYPE)
            elif inputValue['notes'] == 'n':
                dic["NOTES_INSTRUCTION"] = "\n DO NOT generate any notes for slides"
                dic["SAMPLE_JSON"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDHEADING_FORMAT_PROMPT_TYPE)
            
        #check for promptType
        if promptType is None:
            return "PROMPT_NOT_GENERATED"
            
        # construct the prompt from the provided input 
        prompt = Prompt.getPromptAfterProcessing(promptType, dic)
        if prompt is None:
            return "PROMPT_NOT_GENERATED"
        print(prompt)

        # transform the text as per prompt and generate it in json format
        return retryModelForOutputType(sl_role, \
                                prompt, 'json', 'gpt-3.5-turbo', 4096, 2)
    

    @staticmethod    
    def transformTextForQuizGeneration(text, **inputValue):
        system_role = "system" 
        sl_role = Utility.TRASFORMATION_USER_ROLE

        dic = {
            "QUESTION_COUNT": inputValue["questionCount"],
            "DIFFICULTY_LEVEL": inputValue["difficulty"],
            "QUESTION_TYPES_COMMA_SEPARATED": inputValue["questionTypes"],
            "EXPLANATION_INSTRUCTION": "generate an explanation for each question ecxplaining why the correct answer can be derived from the given text. you can take the snippet from the text to explain it." if inputValue["explanation"] == 'y' else ""
        }

        prompt = Prompt.processPrompts(Utility.TRANSFORM_QUIZ_PROMPT_TYPE, dic)
        if prompt is None:
            return "PROMPT_NOT_GENERATED"
        print(prompt)

        # transform the text as per prompt and generate it in json format
        return retryModelForOutputType(sl_role, \
                                prompt, 'json', 'gpt-3.5-turbo', 4096, 2)


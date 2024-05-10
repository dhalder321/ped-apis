import json, uuid, copy
from pathlib import Path
from common.rag import pedRAG
from common.prompts import Prompt
from common.model import (retryModelForOutputType, 
                        getBulkModelResponses,  
                        retryRAGModelForOutputType )
from common.transformModel import generateCriticalAnalysis
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
        # print(prompt)

        # transform the text as per prompt and generate it in html format
        return retryModelForOutputType(sl_role, \
                                prompt, 'html', 'gpt-3.5-turbo', 4096, 2)


    @staticmethod
    def transformTextwithContext(filePath, transformType, **inputValue):

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
                                                    # "TEXT": text,
                                                    "INSTRUCTION": inputValue["instruction"]
                                                    })
        if prompt is None:
            return "PROMPT_NOT_GENERATED"
        # print(prompt)

        # transform the text as per prompt and generate it in html format
        ragModel = pedRAG(maxTokens=4096, maxModelRetry=2)
        colName = ragModel.createVectorCollection(Path(filePath).parent)
        if colName is None:
            return None
        
        retVal = ''
        outputType = ''
        if transformType == 'Critical analysis':
            retVal = generateCriticalAnalysis(ragModel, sl_role, prompt, maxRetry=2)
            outputType = 'TEXT'
        else:
            retVal = retryRAGModelForOutputType(ragModel, sl_role, prompt, maxRetry=2)
            outputType = 'HTML'

        # print(str(retVal))
        return retVal, outputType
        

    @staticmethod    
    def transformTextForPPTGeneration(text, **inputValue):
        system_role = "system" 
        sl_role = Utility.TRASFORMATION_USER_ROLE

        dic = {
            'TEXT': text,
            "CONTENT_INSTRUCTION" : '',
            "NOTES_INSTRUCTION": '',
            "SAMPLE_JSON": '',
            "SLIDE_COUNT": '',
        }

        # set the slide count
        slideCountText = inputValue["slideCount"]
        if "-" in slideCountText:
            slideCountText = slideCountText.replace("-", " and ")
        elif "Default" in slideCountText:
            slideCountText = " 10 and 15 "
        dic['SLIDE_COUNT'] =  slideCountText

        if inputValue["contentType"] == "Summary":
            promptType = Utility.TRANSFORM_PPT_SUMMARY_PROMPT_TYPE
            
        if inputValue["contentType"] == "Full Text":
            promptType = Utility.TRANSFORM_PPT_FULLTEXT_PROMPT_TYPE
        
        if inputValue["format"] == "Text Only":
            dic["CONTENT_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_CONTENT_TEXTONLY_INSTRUCTION_PROMPT_TYPE)
            if inputValue["notes"] == 'y':
                dic["NOTES_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_NOTES_INSTRUCTION_PROMPT_TYPE)
                sample_json = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_TEXT_NOTES_FORMAT_PROMPT_TYPE)
            elif inputValue['notes'] == 'n':
                dic["NOTES_INSTRUCTION"] = "\n DO NOT generate any notes for slides.\n"
                sample_json = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_TEXT_FORMAT_PROMPT_TYPE)

        elif inputValue["format"] == "List with text":
            dic["CONTENT_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_CONTENT_LISTANDTEXTONLY_INSTRUCTION_PROMPT_TYPE)
            if inputValue["notes"] == 'y':
                dic["NOTES_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_NOTES_INSTRUCTION_PROMPT_TYPE)
                sample_json = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDTEXT_NOTES_FORMAT_PROMPT_TYPE)
            elif inputValue['notes'] == 'n':
                dic["NOTES_INSTRUCTION"] = "\n DO NOT generate any notes for slides.\n"
                sample_json = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDTEXT_FORMAT_PROMPT_TYPE)

        elif inputValue["format"] == "List with headings":
            dic["CONTENT_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_CONTENT_LISTANDHEADINGONLY_INSTRUCTION_PROMPT_TYPE)
            if inputValue["notes"] == 'y':
                dic["NOTES_INSTRUCTION"] = Prompt.getPrompt(Utility.TRANSFORM_PPT_NOTES_INSTRUCTION_PROMPT_TYPE)
                sample_json = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDHEADING_NOTES_FORMAT_PROMPT_TYPE)
            elif inputValue['notes'] == 'n':
                dic["NOTES_INSTRUCTION"] = "\n DO NOT generate any notes for slides"
                sample_json = Prompt.getPrompt(Utility.TRANSFORM_PPT_JSON_LISTANDHEADING_FORMAT_PROMPT_TYPE)
            
        #check for promptType
        if promptType is None:
            return "PROMPT_NOT_GENERATED"
        
        # print(dic)
            
        # construct the prompt from the provided input 
        prompt = Prompt.getPromptAfterProcessing(promptType, dic)
        if prompt is None:
            return "PROMPT_NOT_GENERATED"
        # print(prompt)


        #################   ASYNC OPENAI INVOCATION  ########################################
        overridePrompt = Prompt.getPromptAfterProcessing(Utility.TRANSFORM_PPT_OVERRIDE_PROMPT_TYPE, {
            'PROMPT': prompt
        })
        # print("overridePrompt" + overridePrompt + "\n\n")
        # transform the text as per prompt and generate it in json format
        headingsJson = retryModelForOutputType(sl_role, \
                                overridePrompt, 'json', 'gpt-3.5-turbo', 4096, 2)

        print ("headingsJson" + headingsJson + "\n\n")
        # generate individual prompts for each slide.
        # generate a slide id
        slideID = str(uuid.uuid1())

        headings = json.loads(headingsJson)

        if 'title' not in headings or 'headings' not in headings:
            return None
        
        prompts = []
        slideNumber = 1
        iterationNo = 1
        hList = copy.deepcopy(headings['headings'])
        # hList = list(hCopy)
        twoHeadings = []
        results = []
        while True:
            
            # get only 2 prompts in one iteration
            # to avoid reaching Chatgpt's Token per Minute (TPM) threshold 
            startPosition = 2 * (iterationNo - 1)
            if startPosition >= len(hList):
                break

            twoHeadings.clear()
            twoHeadings.append(hList[startPosition])

            if (startPosition + 1) <= (len(hList) - 1):
                twoHeadings.append(hList[startPosition + 1])

            prompts.clear()
            for h in twoHeadings:
                prompts.append(Prompt.getPromptAfterProcessing(Utility.TRANSFORM_PPT_SUBHEADING_PROMPT_TYPE,
                            {
                                'SLIDE_ID': slideID,
                                'SLIDE_NUMBER': str(slideNumber),
                                'SLIDE_HEADING': h,
                                'PROMPT': prompt,
                                'SAMPLE_JSON': sample_json,
                            }))
                slideNumber += 1
                # print(prompts[len(prompts) - 1] + "\n\n")

            tasks = None
            tasks = asyncio.run(getBulkModelResponses(sl_role, prompts, 'gpt-3.5-turbo', 4096))
            if tasks is None or len(tasks) != len(twoHeadings):
                # print ("length of headings:: " + str(len(twoHeadings)))
                # print ("length of tasks:: " + str(len(tasks)))
                return None
            for task in tasks:
                c = task.result()
                c = c.replace("```json", "").replace("```", "") if c is not None else ""
                # print (c)
                results.append(json.loads(c))
                # print ("iteration no: " + str(iterationNo) + " results::" + str(results))
            
            iterationNo += 1
        # print('results:: ' + str(results) + '\n\n')

        # consolidate results
        finalJson = {
            'title': headings['title'],
            'slides': results
        }
        return json.dumps(finalJson)
        #################################################################################


        # # transform the text as per prompt and generate it in json format
        # return retryModelForOutputType(sl_role, \
        #                         prompt, 'json', 'gpt-3.5-turbo', 4096, 2)
    

    @staticmethod    
    def transformTextForQuizGeneration(text, **inputValue):
        system_role = "system" 
        sl_role = Utility.TRASFORMATION_USER_ROLE

        dic = {
            'TEXT': text,
            "QUESTION_COUNT": inputValue["questionCount"],
            "DIFFICULTY_LEVEL": inputValue["difficulty"],
            "QUESTION_TYPES_COMMA_SEPARATED": inputValue["questionTypes"],
            "EXPLANATION_INSTRUCTION": "generate an explanation for each question ecxplaining why the correct answer can be derived from the given text. you can take the snippet from the text to explain it." if inputValue["explanation"] == 'y' else ""
        }

        prompt = Prompt.getPromptAfterProcessing(Utility.TRANSFORM_QUIZ_PROMPT_TYPE, dic)
        if prompt is None:
            return "PROMPT_NOT_GENERATED"
        # print(prompt)

        # transform the text as per prompt and generate it in json format
        return retryModelForOutputType(sl_role, \
                                prompt, 'json', 'gpt-3.5-turbo', 4096, 5)


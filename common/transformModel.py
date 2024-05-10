import time
import json
import logging
import traceback
from common.model import retryRAGModelForOutputType


## This method invokes chat gpt with RAG pipeline and returns a response.
## The response which consists of output text and summary is generated through 
## a sequencial generation pipeline in which summary of the previous tasks are 
## fed to the subsequent tasks - ideal for analysis of text etc. 
def generateCriticalAnalysis(llmObject, system_role, json_prompt, outputType = "text", maxRetry= 2):
    
    #validate inputs
    if system_role is None or json_prompt is None:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in def generateCriticalAnalysis Function: input not provided.")
        return None

    prompts = json.loads(json_prompt)


    taskNo = 1
    consolidated_summary = ''
    outputText = ''

    try:
        while(True):
            
            if taskNo >= len(prompts):
                break

            prompt = ''
            if taskNo == 1:
                # prompt += f" Add section heading as '{prompts[taskNo - 1]['task']}' \n\n"
                prompt = prompts[taskNo - 1]['prompt']
                prompt += "\n\n -----------summary-------------\n\n" + json.dumps(prompts[taskNo]) + "\n\n--------------------\n\n"
            else:
                prompt = prompts[taskNo - 1]['prompt']
                consolidated_summary +=  "\n\n" + jsonval['output']['summary'] if 'summary' in jsonval['output'] else ""
                if 'summaryConsolidated' in prompts[taskNo - 1] and prompts[taskNo - 1]['summaryConsolidated'] == 'y':
                    prompt += "\n\n -----------summary-------------\n\n" + consolidated_summary + "\n\n--------------------\n\n"
                else:
                    prompt += "\n\n -----------summary-------------\n\n" + jsonval['output']['summary'] if 'summary' in jsonval['output'] else "" + "\n\n--------------------\n\n"
                
                prompt += "\n\n" + json.dumps(prompts[taskNo])

            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='json')

            # response = response.replace("```json", "")
            # response = response.replace("```", "")
            jsonval = json.loads(response)
            outputText += "\n\n" + prompts[taskNo - 1]['task']
            outputText += "\n\n" + jsonval['output']['text'] if 'text' in jsonval['output'] else ""
            
            taskNo += 2
            time.sleep(5)

        return outputText
    
    except Exception as e:
        logging.error(f"Error in generateCriticalAnalysis Function: {str(e)}")
        
    return None



## This method invokes chat gpt with RAG pipeline and returns an executive summary.
## "step": 1: Generate an exhaustive list of key points from the document.
## "step": 2: Elaborate on each key point with detailed sentences.
## "step": 3: Generate a concise summary of all key points.
def generateExecutiveSummary(llmObject, system_role, json_prompt, outputType = "text", maxRetry= 2):
    
    try:
        #validate inputs
        if system_role is None or json_prompt is None:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in def generateExecutiveSummary Function: input not provided.")
            return None

        prompts = json.loads(json_prompt)

        # step 1: get the key points
        prompt = prompts[0]['prompt']
        response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='json')
        if response is None:
            return None
        
        keyPoints = json.loads(response)

        # step 2: elaborate key points
        keysText = ''
        keyElaborationPrompt = prompts[1]['prompt']
        outputText = ''
        for key in keyPoints['key points']:
            keysText += key + "\n"

            prompt = keyElaborationPrompt.replace('{{KEY_POINT}}', key)
            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
            if response is None:
                continue

            outputText += response 
            time.sleep(7)

        # step 3: summarize
        summary_prompt = prompts[2]['prompt']
        summary_prompt = summary_prompt.replace('{{KEY_POINTS}}', keysText)
        response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
        if response is not None:
            outputText += "\n\nSummary\n\n" + response

        return outputText
    
    except Exception as e:
        logging.error(f"Error in generateExecutiveSummary Function: {str(e)}")
        
    return None



## This method invokes chat gpt with RAG pipeline and returns subjective questions and answers.
## "step": 1 - Extract key topics from a section of the document.
## "step": 2 - Generate subjective questions and answers based on the topics.
def generateQuestionsNAnswers(llmObject, system_role, json_prompt, outputType = "text", maxRetry= 2):
    
    try:
        #validate inputs
        if system_role is None or json_prompt is None:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in def generateQuestionsNAnswers Function: input not provided.")
            return None

        prompts = json.loads(json_prompt)

        # step 1: get the key points
        prompt = prompts[0]['prompt']
        response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
        if response is None:
            return None
        

        # step 2: generate questions and answers
        prompt = prompts[1]['prompt'].replace('{{SUMMARY}}', response)
        outputText = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
        if outputText is None:
            return None

        return outputText
    
    except Exception as e:
        logging.error(f"Error in generateQuestionsNAnswers Function: {str(e)}")
        
    return None


## This method invokes chat gpt with RAG pipeline and returns objective questions and answers.
## "step": 1 - Extract key topics from a section of the document.
## "step": 2 - Generate objective questions & answers based on the topics.
def generateObjectiveQuestionsNAnswers(llmObject, system_role, json_prompt, 
                                        outputType = "text", maxRetry= 2):
    
    try:
        #validate inputs
        if system_role is None or json_prompt is None:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in def generateObjectiveQuestionsNAnswers Function: input not provided.")
            return None

        prompts = json.loads(json_prompt)

        # step 1: get the key points
        prompt = prompts[0]['prompt']
        response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
        if response is None:
            return None
        

        # step 2: generate questions and answers
        prompt = prompts[1]['prompt'].replace('{{SUMMARY}}', response)
        outputText = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
        if outputText is None:
            return None

        return outputText
    
    except Exception as e:
        logging.error(f"Error in generateObjectiveQuestionsNAnswers Function: {str(e)}")
        
    return None

## This method invokes chat gpt with RAG pipeline and returns list of websites and descriptions.
## "step": 1 - generate website links to blogs, govt sites and so on
## "step": 2 - Generate descriptions for each link.
def generateOnlineReferences(llmObject, system_role, json_prompt, 
                                        outputType = "text", maxRetry= 2):
    
    try:
        #validate inputs
        if system_role is None or json_prompt is None:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in def generateOnlineReferences Function: input not provided.")
            return None

        prompts = json.loads(json_prompt)

        # step 1: get the key points
        prompt = prompts[0]['prompt']
        response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='json')
        if response is None:
            return None
        
        resources = json.loads(response)

        resourceText = ''
        prompt = prompts[1]['prompt']
        outputText = ''
        for r in resources['Online_Resources']:

            resourceText = f"Resource link: {r['link']} \nresource type: {r['type']} \n"
            resourceTextWithDesc = resourceText + "description: {r['description']} \n"
            prompt = prompt.replace('{{ONLINE_RESOURCE}}', resourceTextWithDesc)

            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
            if response is None:
                continue

            outputText += resourceText + "\n\n" +response
            
        return outputText
    
    except Exception as e:
        logging.error(f"Error in generateOnlineReferences Function: {str(e)}")
        
    return None



## This method invokes chat gpt with RAG pipeline and returns list of websites and descriptions.
## "step": 1 - generate website links to blogs, govt sites and so on
## "step": 2 - Generate descriptions for each link.
def generateOnlineReferences(llmObject, system_role, json_prompt, 
                                        outputType = "text", maxRetry= 2):
    
    try:
        #validate inputs
        if system_role is None or json_prompt is None:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in def generateOnlineReferences Function: input not provided.")
            return None

        prompts = json.loads(json_prompt)

        # step 1: get the key points
        prompt = prompts[0]['prompt']
        response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='json')
        if response is None:
            return None
        
        resources = json.loads(response)

        resourceText = ''
        prompt = prompts[1]['prompt']
        outputText = ''
        for r in resources['Online_Resources']:

            resourceText = f"Resource link: {r['link']} \nresource type: {r['type']} \n"
            resourceTextWithDesc = resourceText + "description: {r['description']} \n"
            prompt = prompt.replace('{{ONLINE_RESOURCE}}', resourceTextWithDesc)

            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
            if response is None:
                continue

            outputText += resourceText + "\n\n" +response
            
        return outputText
    
    except Exception as e:
        logging.error(f"Error in generateOnlineReferences Function: {str(e)}")
        
    return None



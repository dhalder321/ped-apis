import time
import json
import logging
import traceback
from common.model import retryRAGModelForOutputType
from common.rag import pedRAG

class transformModel:

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

            prompts = json.loads(json_prompt, strict=False)

            # step 1: get the key points
            prompt = prompts['steps'][0]['prompt']
            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='json')
            if response is None:
                return None
            
            keyPoints = json.loads(response)

            # step 2: elaborate key points
            keysText = ''
            keyElaborationPrompt = prompts['steps'][1]['prompt']
            outputText = ''
            for key in keyPoints['key points']:
                keysText += key + "\n"

                prompt = keyElaborationPrompt.replace('{{KEY_POINT}}', key)
                response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
                if response is None:
                    continue

                outputText += key + "\n\n" 
                outputText += response + "\n\n\n" 
                time.sleep(2)

            # step 3: summarize
            summary_prompt = prompts['steps'][2]['prompt']
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
            prompt = prompts['steps'][0]['prompt']
            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
            if response is None:
                return None
            

            # step 2: generate questions and answers
            prompt = prompts['steps'][1]['prompt'].replace('{{SUMMARY}}', response)
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
            prompt = prompts['steps'][0]['prompt']
            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
            if response is None:
                return None
            

            # step 2: generate questions and answers
            prompt = prompts['steps'][1]['prompt'].replace('{{SUMMARY}}', response)
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
            prompt = prompts['steps'][0]['prompt']
            response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='json')
            if response is None:
                return None
            
            resources = json.loads(response)

            resourceText = ''
            prompt = prompts['steps'][1]['prompt']
            outputText = ''
            for r in resources['Online_Resources']:

                resourceText = f"Resource name: {r['resource name']} \nResource type: {r['type']} \n"
                resourceTextWithDesc = resourceText + "description: {r['description']} \n"
                prompt = prompt.replace('{{ONLINE_RESOURCE}}', resourceTextWithDesc)

                response = retryRAGModelForOutputType(llmObject, system_role, prompt, outputType='text')
                if response is None:
                    continue

                outputText += resourceText + "\n\n" +response + "\n\n\n\n"
                
            return outputText
        
        except Exception as e:
            logging.error(f"Error in generateOnlineReferences Function: {str(e)}")
            
        return None



    ## This method invokes chat gpt with RAG pipeline and returns list of websites and descriptions.
    ## "step": 1 - extract imtroduction, main thesis, key arguments and conclusion sections
    ## "step": 2 - Generate improvement suggestions for each sections
    def generateImprovementSuggestions(llmObject, filePath, system_role, json_prompt, 
                                            outputType = "text", maxRetry= 2):
        
        try:

            #validate inputs
            if system_role is None or json_prompt is None:
                # Log the error with stack trace to CloudWatch Logs
                logging.error(f"Error in def generateImprovementSuggestions Function: input not provided.")
                return None

            prompts = json.loads(json_prompt)
            
            # override the llmobject model as we need 3.5 turbo with specific parameter values
            # create 2 model - one for extraction and one for improvement
            extractionRAG = pedRAG(maxTokens=4095, maxModelRetry=2, temperature=0.3, top_p=1.0,
                                    frequency_penalty=0.0, presence_penalty=0.0)
            collectionName = extractionRAG.createVectorCollection(filePath)

            improvementRAG = pedRAG(maxTokens=4095, maxModelRetry=2, temperature=0.7, top_p=1.0,
                                    frequency_penalty=0.0, presence_penalty=0.0)
            improvementRAG.utilizeVectorCollection(collectionName)


            # step 1: get and generate sugggestions for the introduction
            outputText = ''
            prompt = prompts['Introduction']
            extractionPrompt = prompt['Extraction']['prompt']
            improvementPrompt = prompt['Improvement']['prompt']

            introduction = retryRAGModelForOutputType(extractionRAG, system_role, extractionPrompt, outputType='text')
            if introduction is None:
                return None
            
            improvementPrompt = improvementPrompt.replace('{{INTRODUCTION}}', introduction)
            introImprovementSuggestion = retryRAGModelForOutputType(extractionRAG, system_role, improvementPrompt, outputType='text')

            if introImprovementSuggestion is not None:
                outputText += "Introduction\n\n"
                outputText += introImprovementSuggestion + "\n\n\n\n"

            # step 2: get and generate sugggestions for the thesis section
            prompt = prompts['Thesis Statement']
            extractionPrompt = prompt['Extraction']['prompt']
            improvementPrompt = prompt['Improvement']['prompt']

            thesis = retryRAGModelForOutputType(extractionRAG, system_role, extractionPrompt, outputType='text')
            if thesis is None:
                return None
            
            improvementPrompt = improvementPrompt.replace('{{THESIS_STATEMENT}}', thesis)
            thesisImprovementSuggestion = retryRAGModelForOutputType(extractionRAG, system_role, improvementPrompt, outputType='text')

            if introImprovementSuggestion is not None:
                outputText += "Thesis Statement\n\n"
                outputText += thesisImprovementSuggestion + "\n\n\n\n"

            
            # step 3: get and generate sugggestions for each key arguments
            prompt = prompts['Key Arguments']
            extractionPrompt = prompt['Extraction']['prompt']
            improvementPrompt = prompt['Improvement']['prompt']

            arg = retryRAGModelForOutputType(extractionRAG, system_role, extractionPrompt, outputType='json')
            if arg is None:
                return None
            
            arguments = json.loads(arg)
            argList = arguments['key arguments'] if 'key arguments' in arguments else None
            if argList is None or len(argList) <= 0:
                return None
            
            for a in argList:

                improvementPrompt = improvementPrompt.replace('{{KEY_ARGUMENT}}', a)
                argImprovementSuggestion = retryRAGModelForOutputType(extractionRAG, system_role, improvementPrompt, outputType='text')

                if argImprovementSuggestion is not None:
                    outputText += "Key argument: " + a + "\n\n"
                    outputText += argImprovementSuggestion + "\n\n\n\n"

            # step 4: get and generate sugggestions for the conclusion section
            prompt = prompts['Conclusion']
            extractionPrompt = prompt['Extraction']['prompt']
            improvementPrompt = prompt['Improvement']['prompt']

            conclusion = retryRAGModelForOutputType(extractionRAG, system_role, extractionPrompt, outputType='text')
            if conclusion is None:
                return None
            
            improvementPrompt = improvementPrompt.replace('{{CONCLUSION}}', conclusion)
            conclusionImprovementSuggestion = retryRAGModelForOutputType(extractionRAG, system_role, improvementPrompt, outputType='text')

            if conclusionImprovementSuggestion is not None:
                outputText += "Conclusion\n\n"
                outputText += conclusionImprovementSuggestion + "\n\n"

                
            return outputText
        
        except Exception as e:
            logging.error(f"Error in generateImprovementSuggestions Function: {str(e)}")
        finally:
            if extractionRAG is not None:
                del extractionRAG
            if improvementRAG is not None:
                del improvementRAG
                
        return None


    ## executes the prompt using RAG llm and return response
    def generateContentForPPT(llmObject, system_role, prompt, 
                                            outputType = "text", maxRetry= 2):
        
        #validate inputs
        if prompt is None or llmObject is None:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in def generateContentForPPT Function: input not provided.")
            return None

        try:

            response = retryRAGModelForOutputType(llmObject, system_role, prompt, \
                                                  outputType=outputType, maxRetry=maxRetry)

            return response
        
        except Exception as e:
            logging.error(f"Error in generateContentForPPT Function: {str(e)}")
            
        return None
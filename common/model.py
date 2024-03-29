import os
import json
import logging
import traceback
from openai import OpenAI
from lxml import etree

#client = OpenAI(os.environ["OPENAI_API_KEY"])
client = OpenAI(api_key="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")

def getModelResponse(system_role, user_prompt, llm = "gpt-3.5-turbo", max_tokens=800):

    
    try:

        #validate inputs
        if system_role is None or user_prompt is None or llm is None:
            # Log the error with stack trace to CloudWatch Logs
            logging.error(f"Error in def getModelResponse Function: input not provided.")
            return None
                 
        # Construct the chat messages with roles
        messages = [
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_prompt}
        ]

        # Create the chat completion
        completion = client.chat.completions.create(
            model=llm,
            messages=messages,
            max_tokens=max_tokens
        )

        # Use model_dump() to access the content of the response
        if completion.choices[0].finish_reason == "stop":
            chat_response = completion.choices[0].message.content
            # Return the response
            return chat_response
        else:
            print("Finish reason::" + completion.choices[0].finish_reason)
            raise Exception("Text can not be successfully generated. Finish reason :" + completion.choices[0].finish_reason)
            
    except Exception as e:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in getModelResponse Function: {str(e)}")
        logging.error("Stack Trace:", exc_info=True)


## This method invokes chat gpt LLM and returns a JSON response.
## In case JSON is not in correct format, it will retry for 3 times.
def retryModelForOutputType(system_role, user_prompt, outputType = "text", llm= "gpt-3.5-turbo", \
                            max_tokens=800, maxRetry=3):
    
    #validate inputs
    if system_role is None or user_prompt is None:
        # Log the error with stack trace to CloudWatch Logs
        logging.error(f"Error in def retryModelForOutputType Function: input not provided.")
        return None
    
    if max_tokens <=0: 
        max_tokens = 800
    if maxRetry <= 0:
        maxRetry = 3

    response = getModelResponse(system_role, user_prompt, llm, max_tokens)
    # print(response)
    # logging.debug(response)

    #for output type = text, do not validate
    if outputType == "text":
        return response

    #check for valid json
    for i in range(maxRetry):
        try:

            #check for null output
            if response is None:
                continue

            #check for JSON payload
            if outputType == "json":
                response = response.replace("```json", "")
                response = response.replace("```", "")
                jsonval = json.loads(response)
                return response
            
            elif outputType == "html":
                #remove commonly incorrect text in HTML
                response = response.replace("```html", "")
                response = response.replace("```", "")
                if validateHTML(response):
                    return response
                else:
                    response = getModelResponse(system_role, user_prompt, llm, max_tokens)
                    continue

        except Exception as e:
            logging.error(f"Error in retryModelForOutputType Function: {str(e)}")
            #fix the JSON
            response = getModelResponse(system_role, user_prompt, llm, max_tokens)
            continue
    return None

def validateHTML(html):

    try:
    
    
        # etree.fromstring(html)
        return True
    
    except etree.XMLSyntaxError as e:
        logging.error(f"HTML code is invalid in retryModelForOutputType Function. Error: {str(e)}")
        return False
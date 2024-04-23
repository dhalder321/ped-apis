import time
import json
import logging
import traceback
from openai import OpenAI
from lxml import etree
import asyncio
import aiohttp
import ssl
import certifi

#client = OpenAI(os.environ["OPENAI_API_KEY"])
API_KEY = "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"
client = OpenAI(api_key=API_KEY)

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

# Call ChatGPT with the given prompt, asynchronously.
async def getModelResponseAsync(session, system_role, user_prompt, llm = "gpt-3.5-turbo", max_tokens=800):
    payload = {
        'model': llm,
        "max_tokens": max_tokens,
        'messages': [
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_prompt}
        ]
    }
    try:
        for n in range(3):
            async with session.post(
                url='https://api.openai.com/v1/chat/completions',
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
                json=payload,
                ssl=ssl.create_default_context(cafile=certifi.where())
            ) as response:
                response = await response.json()

            # wait for 5 secs for other threads to complete
            if "error" in response:
                print(f"OpenAI request failed in getModelResponseAsync method with error {response['error']}")
                time.sleep(5)
            else:    
                return response['choices'][0]['message']['content']
    
    except Exception as e:
        print("error in getModelResponseAsync method: " + str(e))

# Call chatGPT for all the given prompts in parallel.
async def getBulkModelResponses(system_role, prompts, llm = "gpt-3.5-turbo", max_tokens=800):

    async with aiohttp.ClientSession() as session, asyncio.TaskGroup() as tg:
    
        responses = \
            [tg.create_task(getModelResponseAsync(session, system_role, prompt, llm, max_tokens)) for prompt in prompts]
    
    return responses


def validateHTML(html):

    try:
    
    
        # etree.fromstring(html)
        return True
    
    except etree.XMLSyntaxError as e:
        logging.error(f"HTML code is invalid in retryModelForOutputType Function. Error: {str(e)}")
        return False
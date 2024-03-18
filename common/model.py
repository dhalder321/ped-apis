import os
import json
import logging
import traceback
from openai import OpenAI

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


    
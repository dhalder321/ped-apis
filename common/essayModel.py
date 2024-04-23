from common.model import retryModelForOutputType, getBulkModelResponses
from common.prompts import Prompt
from common.globals import Utility
import json
import random
import asyncio

# this method geenrates around 3000 to 4000 words for a topic
# takes around 2 - 3 mins
def generateLargeEssayWithMultipleInvokes(system_role, user_prompt, outputType = "text", \
                                          llm= "gpt-3.5-turbo", max_tokens=4095, maxRetry=2):
    

    essayNo = str(random.randrange(10**(7-1), 10**7))
    # set up parent prompt with override prompt encapsulating the user prompt
    parentPrompt = Prompt.getPrompt(Utility.ESSAY_MODEL_OVERRIDE_PROMPT_TYPE).replace('{{ESSAY_NUNBER}}', essayNo) \
                    + user_prompt   

    # get a outline of the essay in JSON
    outline = retryModelForOutputType(system_role, parentPrompt, 'json', llm, max_tokens=2000, maxRetry=2)

    if outline is None:
        return None
    print(outline + "\n\n")

    # iterate through the jSON outline items and generate the essay section by section
    text = ''
    jsonOutline = json.loads(outline)

    #######################OLD CODE- Sequencial OPENAI LIBRARY CALLS############################################
    # Iterate through the dictionary
    # print("Outline::\n" + outline)
    # for heading, points in jsonOutline.items():
    #     text += heading + '\n'
    #     # generate text for heading
    #     # print( Utility.ESSAY_MODEL_HEADING_PROMPT \
    #     #                             .replace('{{HEADING}}',heading).replace('{{ESSAY_NUNBER}}', essayNo))
    #     # t = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_HEADING_PROMPT \
    #     #                             .replace('{{HEADING}}',heading).replace('{{ESSAY_NUNBER}}', essayNo) \
    #     #                             ,'text', max_tokens=1200, maxRetry=2)
    #     # if t is not None:
    #     #     text += t + '\n'
    #     # print (heading + "*******************************************************::\n")

    #     for index, subHeading in enumerate(points, start=1):
    #         #generate text for sub heading
    #         # if heading != subHeading:
    #         #     text += subHeading + '\n'
    #         #generate text for heading
    #         t = retryModelForOutputType(system_role, Prompt.getPrompt(Utility.ESSAY_MODEL_SUBHEADING_PROMPT_TYPE) \
    #                                     .replace('{{SUBHEADING}}',subHeading).replace('{{ESSAY_NUNBER}}', essayNo)\
    #                                     ,'text', max_tokens=1500, maxRetry=2)
    #         if t is not None:
    #             text += t + '\n\n'
    #         # print (subHeading + "*******************************************************::\n" + t)
    ###########################################################################################################

    ############################ NEW CODE- ASYNC & PARALLEL OPENAI API CALLS####################################

    # gather all prompts
    prompts = []
    basePrompt = Prompt.getPrompt(Utility.ESSAY_MODEL_SUBHEADING_PROMPT_TYPE)
    for heading, points in jsonOutline.items():
        for index, subHeading in enumerate(points, start=1):
            prompts.append(basePrompt.replace('{{SUBHEADING}}',subHeading) \
                           .replace('{{ESSAY_NUNBER}}', essayNo) + user_prompt)
    
    # generate results 
    results = []
    startPos = 0
    # process 5 prompts at a time to avoid reaching Chatgpt's TPM threshold
    while True:

        if startPos >= len(prompts):
            break
        print ("startPos::" + str(startPos) +  " Prompt count::" + str(len(prompts)))

        tasks = None
        if (startPos + 4) < (len(prompts) - 1): # more than 5 pending prompts
            tasks = asyncio.run(getBulkModelResponses(system_role, prompts[startPos : startPos + 5], llm, max_tokens))
        elif (startPos + 4) >= (len(prompts) - 1): # five or less prompts pending
            tasks = asyncio.run(getBulkModelResponses(system_role, prompts[startPos : ], llm, max_tokens))
    
        for task in tasks:
            results.append(task.result())

        startPos += 5

    # gather responses
    # match the prompts and chat response counts
    if len(results) != len(prompts):
        return None
    
    for heading, points in jsonOutline.items():
        text += heading + '\n\n'

        for index, subHeading in enumerate(points, start=1):
            if heading != subHeading:
                text += subHeading + '\n\n'

            t = results.pop(0)
            if t is not None:
                text += t + '\n\n'

    ###########################################################################################################

    # convert the text in html
    # print (Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo) + "\n" + text)
    # html = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo)  + "\n" + text \
    #                                 ,'html', max_tokens=4095, maxRetry=2)

    # print(text)
    return text

# this method generates around 1000 - 2000 words for a topic
# takes around 1 min
def generateMediumEssayWithMultipleInvokes(system_role, user_prompt, outputType = "text", \
                                          llm= "gpt-3.5-turbo", max_tokens=4095, maxRetry=2):
    

    essayNo = str(random.randrange(10**(7-1), 10**7))
    # set up parent prompt with override prompt encapsulating the user prompt
    parentPrompt = Prompt.getPrompt(Utility.MEDIUM_ESSAY_MODEL_OVERRIDE_PROMPT_TYPE).replace('{{ESSAY_NUNBER}}', essayNo) \
                    + user_prompt   

    # get a outline of the essay in JSON
    outline = retryModelForOutputType(system_role, parentPrompt, 'json', llm, max_tokens=2000, maxRetry=2)

    if outline is None:
        return None
    print(outline)

    # iterate through the jSON outline items and generate the essay section by section
    text = ''
    jsonOutline = json.loads(outline)

    ################################### OLD CODE- SYNCHRONOUS OPENAI CALLS############################
    # Iterate through the dictionary
    # print("Outline::\n" + outline)
    # for heading, sub_topics in jsonOutline.items():
    #     text += heading + '\n'

    #     for subHeading in sub_topics:
    #         #generate text for sub heading
    #         # if heading != subHeading:
    #         #     text += subHeading + '\n'
    #         #generate text for heading
    #         t = retryModelForOutputType(system_role, Prompt.getPrompt(Utility.MEDIUM_ESSAY_MODEL_SUBHEADING_PROMPT_TYPE) \
    #                                     .replace('{{SUBHEADING}}',subHeading).replace('{{ESSAY_NUNBER}}', essayNo)\
    #                                     ,'text', max_tokens=1500, maxRetry=2)
    #         if t is not None:
    #             text += t + '\n\n'
    #         # print (subHeading + "*******************************************************::\n" + t)
    ######################################################################################################

############################ NEW CODE- ASYNC & PARALLEL OPENAI API CALLS####################################

    # gather all prompts
    prompts = []
    basePrompt = Prompt.getPrompt(Utility.MEDIUM_ESSAY_MODEL_SUBHEADING_PROMPT_TYPE)
    for heading, points in jsonOutline.items():
        for index, subHeading in enumerate(points, start=1):
            prompts.append( basePrompt.replace('{{SUBHEADING}}',subHeading) \
                                .replace('{{ESSAY_NUNBER}}', essayNo) + user_prompt) 
    
    # generate results 
    results = []
    startPos = 0
    # process 5 prompts at a time to avoid reaching Chatgpt's TPM threshold
    while True:

        if startPos >= len(prompts):
            break
        print ("startPos::" + str(startPos) +  " Prompt count::" + str(len(prompts)))

        tasks = None
        if (startPos + 4) < (len(prompts) - 1): # more than 5 pending prompts
            tasks = asyncio.run(getBulkModelResponses(system_role, prompts[startPos : startPos + 5], llm, max_tokens))
        elif (startPos + 4) >= (len(prompts) - 1): # five or less prompts pending
            tasks = asyncio.run(getBulkModelResponses(system_role, prompts[startPos : ], llm, max_tokens))
    
        for task in tasks:
            results.append(task.result())

        startPos += 5

    # gather responses
    # match the prompts and chat response counts
    if len(results) != len(prompts):
        return None
    
    for heading, points in jsonOutline.items():
        text += heading + '\n\n'

        for index, subHeading in enumerate(points, start=1):
            if heading != subHeading:
                text += subHeading + '\n\n'

            t = results.pop(0)
            if t is not None:
                text += t + '\n\n'

    ###########################################################################################################


    # convert the text in html
    # print (Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo) + "\n" + text)
    # html = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo)  + "\n" + text \
    #                                 ,'html', max_tokens=4095, maxRetry=2)

    # print(text)
    return text



# this method generates less than 1000  words for a topic
# takes around 30 secs
def generateShortEssayWithMultipleInvokes(system_role, user_prompt, outputType = "text", \
                                          llm= "gpt-3.5-turbo", max_tokens=4095, maxRetry=2):
    

    essayNo = str(random.randrange(10**(7-1), 10**7))
    # set up parent prompt with override prompt encapsulating the user prompt
    parentPrompt = Prompt.getPrompt(Utility.SHORT_ESSAY_MODEL_OVERRIDE_PROMPT_TYPE).replace('{{ESSAY_NUNBER}}', essayNo) \
                    + user_prompt   
    print(parentPrompt + "\n\n")

    # get a outline of the essay in JSON
    outline = retryModelForOutputType(system_role, parentPrompt, 'json', llm, max_tokens=2000, maxRetry=2)

    if outline is None:
        return None
    print(outline)

    # iterate through the jSON outline items and generate the essay section by section
    text = ''
    jsonOutline = json.loads(outline)

    # Iterate through the dictionary
    # print("Outline::\n" + outline)
    basePrompt = Prompt.getPrompt(Utility.SHORT_ESSAY_MODEL_SUBHEADING_PROMPT_TYPE) 
    for heading, sub_topics in jsonOutline.items():
        text += heading + '\n\n'

        for subHeading in sub_topics:
            #generate text for sub heading
            if heading != subHeading:
                text += subHeading + '\n\n'
            #generate text for heading
            prompt =  basePrompt.replace('{{SUBHEADING}}',subHeading) \
                            .replace('{{ESSAY_NUNBER}}', essayNo) + user_prompt
            t = retryModelForOutputType(system_role, prompt\
                                        ,'text', max_tokens=1500, maxRetry=2)
            if t is not None:
                text += t + '\n\n'
            # print (subHeading + "*******************************************************::\n" + t)

    # convert the text in html
    # print (Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo) + "\n" + text)
    # html = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo)  + "\n" + text \
    #                                 ,'html', max_tokens=4095, maxRetry=2)

    # print(text)
    return text

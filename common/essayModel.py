from common.model import retryModelForOutputType
from common.globals import Utility
import json
import random

# this method geenrates around 3000 to 4000 words for a topic
# takes around 2 - 3 mins
def generateLargeEssayWithMultipleInvokes(system_role, user_prompt, outputType = "text", \
                                          llm= "gpt-3.5-turbo", max_tokens=4095, maxRetry=2):
    

    essayNo = str(random.randrange(10**(7-1), 10**7))
    # set up parent prompt with override prompt encapsulating the user prompt
    parentPrompt = Utility.ESSAY_MODEL_OVERRIDE_PROMPT.replace('{{ESSAY_NUNBER}}', essayNo) \
                    + user_prompt   

    # get a outline of the essay in JSON
    outline = retryModelForOutputType(system_role, parentPrompt, 'json', llm, max_tokens=2000, maxRetry=2)

    if outline is None:
        return None
    
    # iterate through the jSON outline items and generate the essay section by section
    text = ''
    jsonOutline = json.loads(outline)

    # Iterate through the dictionary
    # print("Outline::\n" + outline)
    for heading, points in jsonOutline.items():
        text += heading + '\n'
        # generate text for heading
        # print( Utility.ESSAY_MODEL_HEADING_PROMPT \
        #                             .replace('{{HEADING}}',heading).replace('{{ESSAY_NUNBER}}', essayNo))
        # t = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_HEADING_PROMPT \
        #                             .replace('{{HEADING}}',heading).replace('{{ESSAY_NUNBER}}', essayNo) \
        #                             ,'text', max_tokens=1200, maxRetry=2)
        # if t is not None:
        #     text += t + '\n'
        # print (heading + "*******************************************************::\n")

        for index, subHeading in enumerate(points, start=1):
            #generate text for sub heading
            text += subHeading + '\n'
            #generate text for heading
            t = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_SUBHEADING_PROMPT \
                                        .replace('{{SUBHEADING}}',subHeading).replace('{{ESSAY_NUNBER}}', essayNo)\
                                        ,'text', max_tokens=1500, maxRetry=2)
            if t is not None:
                text += t + '\n'
            # print (subHeading + "*******************************************************::\n" + t)

    # convert the text in html
    # print (Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo) + "\n" + text)
    # html = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo)  + "\n" + text \
    #                                 ,'html', max_tokens=4095, maxRetry=2)

    print(text)
    return text

# this method generates around 1000 - 2000 words for a topic
# takes around 1 min
def generateMediumEssayWithMultipleInvokes(system_role, user_prompt, outputType = "text", \
                                          llm= "gpt-3.5-turbo", max_tokens=4095, maxRetry=2):
    

    essayNo = str(random.randrange(10**(7-1), 10**7))
    # set up parent prompt with override prompt encapsulating the user prompt
    parentPrompt = Utility.MEDIUM_ESSAY_MODEL_OVERRIDE_PROMPT.replace('{{ESSAY_NUNBER}}', essayNo) \
                    + user_prompt   

    # get a outline of the essay in JSON
    outline = retryModelForOutputType(system_role, parentPrompt, 'json', llm, max_tokens=2000, maxRetry=2)

    if outline is None:
        return None
    
    # iterate through the jSON outline items and generate the essay section by section
    text = ''
    jsonOutline = json.loads(outline)

    # Iterate through the dictionary
    # print("Outline::\n" + outline)
    for heading, sub_topics in jsonOutline.items():
        text += heading + '\n'

        for subHeading in sub_topics:
            #generate text for sub heading
            text += subHeading + '\n'
            #generate text for heading
            t = retryModelForOutputType(system_role, Utility.MEDIUM_ESSAY_MODEL_SUBHEADING_PROMPT \
                                        .replace('{{SUBHEADING}}',subHeading).replace('{{ESSAY_NUNBER}}', essayNo)\
                                        ,'text', max_tokens=1500, maxRetry=2)
            if t is not None:
                text += t + '\n'
            # print (subHeading + "*******************************************************::\n" + t)

    # convert the text in html
    # print (Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo) + "\n" + text)
    # html = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo)  + "\n" + text \
    #                                 ,'html', max_tokens=4095, maxRetry=2)

    print(text)
    return text



# this method generates less than 1000  words for a topic
# takes around 30 secs
def generateShortEssayWithMultipleInvokes(system_role, user_prompt, outputType = "text", \
                                          llm= "gpt-3.5-turbo", max_tokens=4095, maxRetry=2):
    

    essayNo = str(random.randrange(10**(7-1), 10**7))
    # set up parent prompt with override prompt encapsulating the user prompt
    parentPrompt = Utility.SHORT_ESSAY_MODEL_OVERRIDE_PROMPT.replace('{{ESSAY_NUNBER}}', essayNo) \
                    + user_prompt   

    # get a outline of the essay in JSON
    outline = retryModelForOutputType(system_role, parentPrompt, 'json', llm, max_tokens=2000, maxRetry=2)

    if outline is None:
        return None
    
    # iterate through the jSON outline items and generate the essay section by section
    text = ''
    jsonOutline = json.loads(outline)

    # Iterate through the dictionary
    # print("Outline::\n" + outline)
    for heading, sub_topics in jsonOutline.items():
        text += heading + '\n'

        for subHeading in sub_topics:
            #generate text for sub heading
            text += subHeading + '\n'
            #generate text for heading
            t = retryModelForOutputType(system_role, Utility.SHORT_ESSAY_MODEL_SUBHEADING_PROMPT \
                                        .replace('{{SUBHEADING}}',subHeading).replace('{{ESSAY_NUNBER}}', essayNo)\
                                        ,'text', max_tokens=1500, maxRetry=2)
            if t is not None:
                text += t + '\n'
            # print (subHeading + "*******************************************************::\n" + t)

    # convert the text in html
    # print (Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo) + "\n" + text)
    # html = retryModelForOutputType(system_role, Utility.ESSAY_MODEL_FINAL_HTML_PROMPT \
    #                                 .replace('{{ESSAY_NUNBER}}', essayNo)  + "\n" + text \
    #                                 ,'html', max_tokens=4095, maxRetry=2)

    print(text)
    return text

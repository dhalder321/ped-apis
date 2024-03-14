import json
from common.model import getModelResponse
from common.s3File import uploadFile, downloadFile, deleteFile
from common.prompts import Prompt
from common.globals import Utility
from topic2summaries import generateSummariesFromTopic
from outlineOfTopic import generateOutlineFromTopic
from textOfTopicOutline import generateTextOfTopicOutline


# text = getModelResponse("You are a biology professor", "write 20 words on acroporus")
# print(text)

# fileURL = uploadFile('dashboard-edited.png', 'pedbuc', 'prompts/dev/dashboard-edited.png')
# print(fileURL)


# downloadFile('dashboardV2.png', 'pedbuc', 'prompts/dev/dashboard-edited.png')

# deleteFile('pedbuc', 'prompts/dev/dashboard-edited.png')

# prmpt = getPrompt(TOPIC2SUMMARY_PROMPT_TYPE)
# print(prmpt)

# data = generateSummariesFromTopic({
#     "body": """{
#         "transactionId": "6932874iruwe764283",
#         "role": "Economics professor",
#         "topic": "recent research on globalization"
#     }"""
#     }, {})
# # print(data)
# print(json.loads(json.loads(data['body'])['Response']))


# data = generateOutlineFromTopic({
#         "body": """{
#         "transactionId": "6932874iruwe764283",
#         "role": "Economics professor",
#         "topic": "recent research on globalization",
#         "summary": "From a political perspective, studies show that globalization has challenged traditional notions of state sovereignty and governance, leading to both increased cooperation and conflict among nations in efforts to navigate the complex global economic landscape."
#     }"""
# }, {})
# #print(data)
# print(json.loads(data['body'])['Response'])


# data = generateTextOfTopicOutline({
#         "body": """{
#         "transactionId": "6932874iruwe764283",
#         "role": "Economics professor",
#         "topic": "recent research on globalization",
#         "summary": "From a political perspective, studies show that globalization has challenged traditional notions of state sovereignty and governance, leading to both increased cooperation and conflict among nations in efforts to navigate the complex global economic landscape."
#     }"""
# }, {})
# #print(data)
# print(json.loads(data['body'])['Response'])

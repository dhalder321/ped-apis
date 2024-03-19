import json
from common.model import getModelResponse
from common.s3File import uploadFile, downloadFile, deleteFile, readFile
from common.prompts import Prompt
from common.globals import Utility
from topic2summaries import generateSummariesFromTopic
from outlineOfTopic import generateOutlineFromTopic
from textOfTopicOutline import generateTextOfTopicOutline
from fileTextSave import saveDocumentFile
from common.db import DBManager
from signup import signupNewUser
from newAccesKey import getAccessKey
from login import loginUserWithemail
from loginWithAccessKey import loginUserWithAccessKey

# text = getModelResponse("You are a biology professor", "write 20 words on acroporus")
# print(text)

# fileURL = uploadFile('dashboard-edited.png', 'pedbuc', 'prompts/dev/dashboard-edited.png')
# print(fileURL)


# downloadFile('dashboardV2.png', 'pedbuc', 'prompts/dev/dashboard-edited.png')

# print(readFile('pedbuc', 'prompts/dev/TEXT2TOPICOUTLINE.txt'))
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


req = {
        "body": """{
        "transactionId": "6932874iruwe764283",
        "userid": "2",
        "role": "Economics professor",
        "topic": "recent research on globalization",
        "summary": "From a political perspective, studies show that globalization has challenged traditional notions of state sovereignty and governance, leading to both increased cooperation and conflict among nations in efforts to navigate the complex global economic landscape.",
        "requesttimeinUTC": "3/14/2024 21:18"
    }"""}
data = generateOutlineFromTopic(req, {})
print(data)
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


# html = '''<!DOCTYPE html>
#                     <html lang="en">
#                     <head>
#                     <meta charset="UTF-8">
#                     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                     <title>Tigers</title>
#                     </head>
#                     <body>
#                     <h1>Tigers</h1>
#                     <p>Tigers, scientifically known as Panthera tigris, are majestic creatures that belong to the cat family, Felidae. They are renowned for their striking orange coat with black stripes, making them one of the most recognizable animals in the world.</p>
#                     <p>These magnificent predators are primarily found in various habitats across Asia, from dense forests to grasslands. Tigers are solitary animals, preferring to hunt alone under the cover of darkness, using their keen senses of sight and hearing to stalk and ambush their prey.</p>
#                     <p>Unfortunately, tigers are endangered due to various factors such as habitat loss, poaching, and human-wildlife conflict. Conservation efforts are underway globally to protect these iconic animals and their habitats.</p>
#                     <p>Efforts such as establishing protected areas, anti-poaching measures, and community involvement are crucial for ensuring the survival of tigers in the wild.</p>
#                     <p>In conclusion, tigers are not only magnificent creatures but also vital components of their ecosystems. It is our responsibility to work towards their conservation and ensure that future generations can admire these majestic beasts in their natural habitats.</p>
#                     </body>
#                     </html>
#                 '''
# req = {
#         "userid": "18876",
#         "transactionId": "6932874iruwe764283",
#         "text": html,
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }

# data = saveDocumentFile({
#         "body": json.dumps(req)
# }, {})
# print(data)
# print(json.loads(data['body'])['Response']))

# print(DBManager.get_highest_fileid("ped-userfiles", "staticIndexColumn", "fileid", \
#                              "staticIndexColumn-fileid-index"))

# DBManager.updateRecordInDynamoTable("ped-useractivity", "activityid", "1", "userid", "18876", {
# })


# req = {
#         "firstName": "Thomas",
#         "lastName": "Linder",
#         "email": "tlinder@gmail.com",
#         "pwdEn": "*!^@&*^$kjhsdf9873r", 
#         "transactionId": "91849184714o31rij3984",
#         "requesttimeinUTC": "3/17/2024 21:18"
#     }
# req = {
#         "body": json.dumps(req)
# }
# data = signupNewUser({
#         "body": json.dumps(req)
# }, {})
# print(data)


# req = {
#         "userid": "1",
#         "transactionId": "23984ewfkj928r23",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }
# data = getAccessKey({
#         "body": json.dumps(req)
# }, {})
# print(data)


# req = {
#         "email": "cvraman1@gmail.com",
#         "pwdEn": "^%*&$(*&!@dskjvkds)", 
#         "transactionId": "8736423hk2j3483",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }
# data = signupNewUser({
#         "body": json.dumps(req)
# }, {})
# print(data)


# req = {
#         "email": "dhalder@gmail.com",
#         "pwdEn": "^%*&$(*&!@dskjvkds)", 
#         "transactionId": "8736423hk2j3483",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }
# data = loginUserWithemail({
#         "body": json.dumps(req)
# }, {})
# print(data)


# response = DBManager.getDBItems(
#         table_name='ped-users',
#         # partition_key_name="userid",
#         # partition_key_value="3",
#         sort_key_name="email",
#         sort_key_value="dhalder@gmail.com",
#         filter_expression='pwdEn = :value',
#         value="^%*&$(*&!@dskjvkds)", 
#         projection_expression='userid, firstName, lastName',
#         index_name="email-index"
#     )
# print (response)


# req = {
#         "asseccKey": "VW2PUS",
#         "transactionId": "8736423hk2j3483",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }
# data = loginUserWithAccessKey({
#         "body": json.dumps(req)
# }, {})
# print(data)


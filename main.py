import json
from common.model import getModelResponse
from common.s3File import uploadFile, downloadFile, deleteFile
from common.prompts import Prompt
from common.globals import Utility
from topic2summaries import generateSummariesFromTopic
from outlineOfTopic import generateOutlineFromTopic
from textOfTopicOutline import generateTextOfTopicOutline
from fileTextSave import saveDocumentFile


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


html = '''<!DOCTYPE html>
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Tigers</title>
                    </head>
                    <body>
                    <h1>Tigers</h1>
                    <p>Tigers, scientifically known as Panthera tigris, are majestic creatures that belong to the cat family, Felidae. They are renowned for their striking orange coat with black stripes, making them one of the most recognizable animals in the world.</p>
                    <p>These magnificent predators are primarily found in various habitats across Asia, from dense forests to grasslands. Tigers are solitary animals, preferring to hunt alone under the cover of darkness, using their keen senses of sight and hearing to stalk and ambush their prey.</p>
                    <p>Unfortunately, tigers are endangered due to various factors such as habitat loss, poaching, and human-wildlife conflict. Conservation efforts are underway globally to protect these iconic animals and their habitats.</p>
                    <p>Efforts such as establishing protected areas, anti-poaching measures, and community involvement are crucial for ensuring the survival of tigers in the wild.</p>
                    <p>In conclusion, tigers are not only magnificent creatures but also vital components of their ecosystems. It is our responsibility to work towards their conservation and ensure that future generations can admire these majestic beasts in their natural habitats.</p>
                    </body>
                    </html>
                '''
req = {
        "userid": "18876",
        "transactionId": "6932874iruwe764283",
        "text": html,
        "requesttimeinUTC": "3/14/2024 21:18"
    }

data = saveDocumentFile({
        "body": json.dumps(req)
}, {})
print(data)
#print(json.loads(data['body'])['Response']))

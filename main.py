import json
import base64
from common.model import getModelResponse, retryModelForOutputType, getBulkModelResponses
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
from ppt2text import generateDocumentFromPresentation
from doc2Text import generateDocumentFromDocument
from text2text import generateDocumentFromText
from pdf2text import generateDocumentFromPDF
from web2text import generateDocumentFromWebContent
from ppt2video import generateVideoFromPresentation
from ppt2image import getImagesFromPPT
from docOfTopicOutline import generateDocOfTopicOutline
from quickText import generateQuickText
from doc2PPT import generatePPTFromDocument
from doc2quiz import generateQuizFromDocument
from verifyDoc4Transformation import verifyDocument

# text = getModelResponse("You are a biology professor", "write 20 words on acroporus")
# print(text)

# text = retryModelForOutputType("You are a biology professor", \
#                                'write top 5 points on tigers in JSON format {"1": "point 1"}', "json")
# print(text)

# text = retryModelForOutputType("You are a biology professor", \
#                                '''write 600 lines on tigers. convert the text into HTML.
#                                HTML output should have at minimum Doctype, HTML, 
#                                head, body tags. Only emit the HTML and no other text''', "html")
# print(text)

# fileURL = uploadFile('dashboard-edited.png', 'pedbuc', 'prompts/dev/dashboard-edited.png')
# print(fileURL)


# downloadFile('dashboardV2.png', 'pedbuc', 'prompts/dev/dashboard-edited.png')

# print(readFile('pedbuc', 'prompts/dev/TEXT2TOPICOUTLINE.txt'))
# deleteFile('pedbuc', 'prompts/dev/dashboard-edited.png')

# prmpt = getPrompt(TOPIC2SUMMARY_PROMPT_TYPE)
# print(prmpt)

# data = generateSummariesFromTopic({
#     "httpMethod" : "POST",
#     "body": """{
#         "transactionId": "6932874iruwe764283",
#         "userid": "223",
#         "role": "Economics professor",
#         "topic": "recent research on globalization",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }"""
#     }, {})
# print(data)
# print(json.loads(json.loads(data['body'])['Response']))

# req = {
#         "httpMethod" : "POST",
#         "body": """{
#         "transactionId": "6932874iruwe764283",
#         "userid": "2",
#         "role": "Economics professor",
#         "topic": "recent research on globalization",
#         "summary": "From a political perspective, studies show that globalization has challenged traditional notions of state sovereignty and governance, leading to both increased cooperation and conflict among nations in efforts to navigate the complex global economic landscape.",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }"""}
# data = generateOutlineFromTopic(req, {})
# print(data)
# print(json.loads(data['body'])['Response'])


# data = generateTextOfTopicOutline({
#         "httpMethod" : "POST",
#         "body": """{
#         "transactionId": "6932874iruwe764283",
#         "userid": "2",
#         "role": "Political science professor",
#         "topic": "Modi govt's contribution in Indian politics",
#         "summary": "",
#         "outline": "",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }"""
# }, {})
# print(data)


# data = generateDocOfTopicOutline({
#         "httpMethod" : "POST",
#         "body": """{
#         "transactionId": "KHIHo4y29852c24c24c2",
#         "userid": "2",
#         "role": "Political science professor",
#         "topic": "Modi govt's contribution in Indian politics",
#         "summary": "",
#         "outline": "",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }"""
# }, {})
# print(data)
# print(json.loads(data['body'])['Response'])


# data = generateQuickText({
#         "httpMethod" : "POST",
#         "body": """{
#         "transactionId": "KHIHo4y29852c24c24c2",
#         "userid": "2",
#         "role": "astronomy professor",
#         "topic": "Pluto's role in solar system",
#         "essaySize": "l",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }"""
# }, {})
# print(data)
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


# read  file ppt file in base64 format
# with open("G:\\My Drive\\GEMBA Course Content\\Final Project\\Pitch-V2\\Materials\\IndianPolitics.docx", \
#             "rb") as f:
#     bytes = f.read()
# req = {
#         "userid": "34454",
#         "transactionId": "6932874iruwe764283",
#         "text": "",
#         "fileContentInBase64": base64.b64encode(bytes).decode('utf-8'),
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }

# data = saveDocumentFile({
#         "httpMethod": "POST",
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

# read  file ppt file in base64 format
# with open("G:\\My Drive\\GEMBA Course Content\\Final Project\\Pitch-V2\\Materials\\The Modi Phenomenon and the Re making of India.pdf", \
#             "rb") as f:
#     bytes = f.read()
# #print(base64.b64encode(bytes).decode('utf-8'))
# req = {
#         "fileContentBase64": base64.b64encode(bytes).decode('utf-8'),
#         "fileName": "humanrights.pdf", 
#         "renderingType": "Critical analysis instruction",
#         "instruction": "generate it for first year college students.",
#         "userid": "12289",
#         "transactionId": "8736423hk2j3483",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }
# # print (req)
# data = generateDocumentFromPDF({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)


# req = {
#         "url": "https://www.cdc.gov/disasters/volcanoes/facts.html", 
#         "renderingType": "Critical analysis",
#         "instruction": "generate it for first year college students.",
#         "userid": "23322",
#         "transactionId": "aksfjnar832764832",
#         "requesttimeinUTC": "3/29/2024 21:18"
#     }
# # print (req)
# data = generateDocumentFromWebContent({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)
 

#  read  file ppt file in base64 format
# with open("G:\\My Drive\\GEMBA Course Content\\Final Project\\Pitch-V2\\Materials\\BritishCrueltyInIndia.docx", \
#             "rb") as f:
#     bytes = f.read()
# req = {
#         "fileContentBase64": base64.b64encode(bytes).decode('utf-8'),
#         "fileName": "GenghisKhan.docx", 
#         "userid": "23343",
#         "slideCount": "Default", # 5-10, 10-15
#         "contentType": "Summary", #"Full Text",
#         "format": "Text Only", #"List with headings", #"List with text", #"Text Only",
#         "notes": "y",
#         "transactionId": "98327402lkjsdf33effe",
#         "requesttimeinUTC": "4/12/2024 21:18"
#     }
# # print (req)
# data = generatePPTFromDocument({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)

#  read  file ppt file in base64 format
# with open("G:\\My Drive\\GEMBA Course Content\\Final Project\\Pitch-V2\\Materials\\Globalization.docx", \
#             "rb") as f:
#     bytes = f.read()
# req = {
#         "fileContentBase64": base64.b64encode(bytes).decode('utf-8'),
#         "fileName": "humanrights.docx", 
#         "userid": "334433",
#         "qestionCount": "5-10", # 5-10, 10-15, if Default selected, set q count :- 15-20
#         "difficulty": "simple", # "simple", "medium", "hard", "very hard"
#         "questionType": "multiple choice, true/false, fill the blanks, ranking/ordering",
#         "explanation": "y",
#         "transactionId": "98327402lkjsdf33effe",
#         "requesttimeinUTC": "4/12/2024 21:18"
#     }
# # print (req)
# data = generateQuizFromDocument({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)

#  read  file ppt file in base64 format
with open("G:\\My Drive\\GEMBA Course Content\\Final Project\\Pitch-V2\\Materials\\Globalization.docx", \
            "rb") as f:
    bytes = f.read()
req = {
        "fileContentBase64": base64.b64encode(bytes).decode('utf-8'),
        "fileName": "humanrights.docx", 
        "userid": "334433",
        "transactionId": "98327402lkjsdf33effe",
        "requesttimeinUTC": "4/12/2024 21:18"
    }
# print (req)
data = verifyDocument({
        "httpMethod": "POST",
        "body": json.dumps(req)
}, {})
print(data)


#  read  file ppt file in base64 format
# with open("G:\\My Drive\\GEMBA Course Content\\Final Project\\Pitch-V2\\Materials\\Mastering Crowd Funding.pptx", \
#             "rb") as f:
#     bytes = f.read()
# req = {
#         "fileContentBase64": base64.b64encode(bytes).decode('utf-8'),
#         "fileName": "humanrights.pptx", 
#         "userid": "67745",
#         "transactionId": "8736423hk2j3483",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }
# # print (req)
# data = generateVideoFromPresentation({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)

# getImagesFromPPT("c:\\users\\dhalde\\Brazil's Top Tourist Destinations.pptx")



# prompts = ["one", "two", "three", "four"]
# results = asyncio.run(getBulkModelResponses("you are a mathematician", prompts))
# # print(results)
# for t in results:
#     print("result:" + t.result())



import json, requests
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
from generateemailcode import generateEmailVerificationCode
from verifyemailcode import verifyEmailVerificationCode
from getQuizInDoc import getQuizInDocument
from getQuizJSON import getQuizJSON

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
#         "transactionId": "728364293kjhfsd98r73",
#         "priorTranIds": "",
#         "userid": "123456",
#         "role": "hindi professor",
#         "topic": "Critical Analysis of tagore's work",
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
#         "email": "debjit.halder.bbsr@gmail.com",
#         "transactionId": "91849184714o31rij3984",
#         "requesttimeinUTC": "3/17/2024 21:18"
#     }
# data = generateEmailVerificationCode({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)

# req = {
#         "email": "debjit.halder.bbsr@gmail.com",
#         "emailCode" : "460618",
#         "transactionId": "91849184714o31rij3984",
#         "requesttimeinUTC": "3/17/2024 21:18"
#     }
# data = verifyEmailVerificationCode({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)


# req = {
#         "userid": "1",
#         "transactionId": "23984ewfkj928r23",
#         "requesttimeinUTC": "3/14/2024 21:18"
#     }
# data = getAccessKey({
#         "httpMethod": "POST",
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
#         "userid": "334400",
#         "transactionId": "djkfdsr93875932-2523523v235v-23523v5vv325",
#         "renderingType": "Study guide", 
#         "instruction": "",
#         "text": "Democracy, derived from the Greek words \"demos\" (people) and \"kratos\" (rule), embodies a system of governance where power resides with the people. This form of government promotes political equality, participation, and representation. At its core, democracy fosters the idea of collective decision-making, ensuring that the interests and voices of citizens shape policies and laws.   One of democracy's fundamental principles is the protection of individual rights and freedoms. Through mechanisms such as free speech, assembly, and press, citizens can express themselves without fear of repression. Moreover, democratic systems establish an independent judiciary to safeguard against abuses of power, ensuring justice and accountability. Furthermore, democracy promotes transparency and accountability in governance. Elected representatives are accountable to the electorate, and periodic elections serve as mechanisms for citizens to hold their leaders responsible for their actions. Additionally, democratic institutions, such as the legislature and executive branches, operate under checks and balances, preventing any single entity from monopolizing power. Moreover, democracy encourages political participation and civic engagement. Citizens have the right to vote, allowing them to choose their leaders and influence public policies. Furthermore, democratic societies foster a vibrant civil society, comprising non-governmental organizations, advocacy groups, and grassroots movements that contribute to public discourse and policymaking. Despite its merits, democracy faces challenges and criticisms. Issues such as voter apathy, political polarization, and the influence of money in politics can undermine its effectiveness. Moreover, in some cases, democratic processes may lead to the tyranny of the majority, where the rights of minority groups are disregarded. In conclusion, democracy serves as a cornerstone of modern governance, embodying principles of political equality, participation, and representation. By empowering citizens, protecting individual rights, and promoting accountability, democracy fosters a society where the voices of the people shape the course of their nation. However, it requires continuous vigilance and active participation to ensure its vitality and effectiveness in addressing the evolving needs of society.",
#         "requesttimeinUTC": "4/14/2024 21:18"
#     }
# # print (req)
# data = generateDocumentFromText({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)

# req = {
        # "url": "https://www.cdc.gov/disasters/volcanoes/facts.html", 
        # "renderingType": "Critical analysis",
        # "instruction": "generate it for first year college students.",
        # "userid": "23322",
        # "transactionId": "aksfjnar832764832",
        # "requesttimeinUTC": "3/29/2024 21:18"
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
# # print (base64.b64encode(bytes).decode('utf-8'))
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
#         "userid": "90009",
#         "qestionCount": "15-20", # 5-10, 10-15, if Default selected, set q count :- 15-20
#         "difficulty": "simple", # "simple", "medium", "hard", "very hard"
#         "questionType": "multiple choice, true/false, fill the blanks, ranking/ordering",
#         "explanation": "y",
#         "transactionId": "324723904780324314",
#         "requesttimeinUTC": "4/29/2024 21:18"
#     }
# # print (req)
# data = generateQuizFromDocument({
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
#         "transactionId": "98327402lkjsdf33effe",
#         "requesttimeinUTC": "4/12/2024 21:18"
#     }
# # print (req)
# data = verifyDocument({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)


#  read  file ppt file in base64 format
# with open("G:\\My Drive\\GEMBA Course Content\\Final Project\\Pitch-V2\\Materials\\Mastering Crowd Funding.pptx", \
#             "rb") as f:
#     bytes = f.read()
# print(base64.b64encode(bytes).decode('utf-8'))
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

# NOT WORKING CODE.
# url = 'https://ky45lpx7ng.execute-api.us-east-2.amazonaws.com/default/ped-doc2sfdt'
# data = '/mnt/ped/287987/DocumentFile_KHIHo4y29852c24c24c2_04082024193322.docx'
# headers = {"Content-Type": "text/plain"}
# response = requests.post(url, data=data, headers=headers)
# print(response)


# req = {
#         "quizFileId": "307", 
#         "userid": "90009",
#         "transactionId": "sjdfh72394238c23",
#         "requesttimeinUTC": "4/29/2024 21:18"
#     }
# # print (req)
# data = getQuizInDocument({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)


# req = {
#         "quizFileId": "307", 
#         "userid": "90009",
#         "transactionId": "sjdfh72394238c23",
#         "requesttimeinUTC": "4/29/2024 21:18"
#     }
# # print (req)
# data = getQuizJSON({
#         "httpMethod": "POST",
#         "body": json.dumps(req)
# }, {})
# print(data)
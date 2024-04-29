import base64
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']
SERVICE_ACCOUNT_FILE = "ped-apis-v2-gmail-720a468dc829.json"
SERVICE_ACCOUNT_FILEPATH = "/mnt/ped"
SERVICE_ACCOUNT_LOCALFILEPATH = ""

def sendCompanyEmail(emailSender, emailReceiver, subject, emailBody):

  creds = None
  creds = service_account.Credentials.from_service_account_file (
    filename= str(Path(SERVICE_ACCOUNT_FILEPATH, SERVICE_ACCOUNT_FILE)),
    # filename= str(Path(SERVICE_ACCOUNT_LOCALFILEPATH, SERVICE_ACCOUNT_FILE)),
    scopes = SCOPES,
    # subject = "ped-gmail-serv-acc@ped-apis-v2.iam.gserviceaccount.com"
    subject = emailSender
  )
  try:

    service = build("gmail", "v1", credentials=creds)
    message = MIMEText(emailBody)
    message['to'] = emailReceiver
    message['from'] = emailSender
    message['subject'] = subject
    emailPackage = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    send_message = (service.users().messages().send(userId="me", body=emailPackage)
                    .execute())

    print(f'Message Id: {send_message["id"]}')

  except HttpError as error:
    
    print(f"An error occurred: {error}")
    send_message = None
  
  return send_message


if __name__ == "__main__":
  sendCompanyEmail("debjit.halder.bbsr@gmail.com", "459987 - Pioneer Education - email verification code", "233433 - Pioneer education Tech - email verification code")
  
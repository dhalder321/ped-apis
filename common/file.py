from common.prompts import Prompt
from common.model import retryModelForOutputType
from common.globals import Utility
from pptx import Presentation
from docx import Document
import os
from pathlib import Path
import logging
import fitz


def getTextFromPPTX(pptFilePath):

    # check for file existance
    isExist = os.path.exists(pptFilePath)
    if not isExist:    
        return None     

    #check for PPTX file
    fileExtension = Path(pptFilePath).suffix
    if fileExtension != ".pptx":
        return None

    text = ""

    try:
        # get every text section of every slide and 
        # get the text 
        prs = Presentation(pptFilePath)
        for slide in prs.slides:
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        text = text + "\n" + run.text
            #TODO: get the text from slide notes
    
        return text
    
    except Exception as e:
        logging.error(e)
        return None


def getTextFromDoc(docFilePath):

     # check for file existance
    isExist = os.path.exists(docFilePath)
    if not isExist:    
        return None     

    #check for docx file
    fileExtension = Path(docFilePath).suffix
    if fileExtension != ".docx":
        return None

    document = Document(docFilePath)
    full_text = []
    for paragraph in document.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def getTextFromPDF(pdfFilePath):

    # check for file existance
    isExist = os.path.exists(pdfFilePath)
    if not isExist:    
        return None     

    #check for docx file
    fileExtension = Path(pdfFilePath).suffix
    if fileExtension != ".pdf":
        return None

    # Open the PDF file using fitz.open()
    doc = fitz.open(pdfFilePath)
    pageText = ""
    for page in range(doc.page_count):
        pageText += doc.load_page(page).get_text("text") + "\n"
    doc.close()

    return pageText

def getAudioScripts(pptFilePath):

    # check for file existance
    isExist = os.path.exists(pptFilePath)
    if not isExist:    
        return None     

    #check for PPTX file
    fileExtension = Path(pptFilePath).suffix
    if fileExtension != ".pptx":
        return None

    try:
        # check the notes section for each slide
        # if there is no notes, generate and set a note from the slide text
        # save the notes as audio script in the ./script folder

        scriptFileLocation = str(Path(Path(pptFilePath).parent, "script"))
        prs = Presentation(pptFilePath)
        slideCount = 1
        for slide in prs.slides:
            slideText = ''
            slideNote = ''
            if slide.notes_slide is not None and \
                slide.notes_slide.notes_text_frame is not None:

                slideNote = slide.notes_slide.notes_text_frame.text

            if slideNote is None or slideNote == '':
                # get the slide text
                for shape in slide.shapes:
                    if not shape.has_text_frame:
                        continue
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            slideText = slideText + "\n" + run.text
            
                # generate and set a note
                prompt = Prompt.getPrompt(Utility.SLIDE_NOTE_FOR_VIDEO_PROMPT_TYPE) 
                if prompt is None:
                    raise Exception("Prompt could not be generated for slide note generation in checkOrModifyPPT4VideoGeneration method")
                
                prompt += "\n" + slideText

                slideNote = retryModelForOutputType(Utility.TRASFORMATION_USER_ROLE, prompt, 'text', maxRetry= 2)

                if slideNote is not None and slideNote != '':
                    slide.notes_slide.notes_text_frame.text = slideNote

            # save the node text in script folder
            scriptFileName = str(slideCount) + ".txt"
            scriptFilePath = Path(scriptFileLocation, scriptFileName)
            Path(scriptFilePath).mkdir(parents=True, exist_ok=True)
            with scriptFilePath.open("w", encoding ="utf-8") as f:
                f.write(slideNote)

            slideCount += 1    

        prs.save()
    
        return str(scriptFilePath)
    
    except Exception as e:
        logging.error(e)
        return None

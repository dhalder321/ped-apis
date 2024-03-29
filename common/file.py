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

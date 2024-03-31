import win32com.client
import os

# Create a PowerPoint application object
Application = win32com.client.Dispatch("PowerPoint.Application")

def getImagesFromPPT(pptFilePath):
    try:
        # Open the presentation without making it visible
        Presentation = Application.Presentations.Open(pptFilePath, WithWindow=False)

        # Create a folder to save the slides as images
        imageFilePath = os.path.join(os.path.dirname(pptFilePath), "images")
        if not os.path.exists(imageFilePath):
            os.makedirs(imageFilePath)

        # Export each slide as an image
        for i, slide in enumerate(Presentation.Slides):
            image_path = os.path.join(imageFilePath, f"{i + 1}.png")
            slide.Export(image_path, "JPG")
            

        # Close the presentation
        Presentation.Close()

        return imageFilePath
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    #finally:
        # Quit the PowerPoint application
        #Application.Quit()

from gtts import gTTS
import os, logging
from pathlib import Path

def generateVoiceOverFiles(scriptFilePath, audioFilePath):

    try:
        # check both paths
        scriptPath = Path(scriptFilePath)
        if not scriptPath.exists() or not any(scriptPath.iterdir()):
            return "INVALID_SCRIPT_LOCATION"
        
        audioPath = Path(audioFilePath)
        if not audioPath.exists():
            audioPath.mkdir()

        # Process each text file in the input directory
        for filename in os.listdir(scriptFilePath):
            if filename.endswith('.txt'):  # Ensure processing only text files
                file_path = os.path.join(scriptFilePath, filename)
                
                # Read the text from the file
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()

                # Convert text to speech
                # tts = gTTS(text=text, lang='en-in', slow=False)
                
                # # Save the audio file in the output directory with the same name as the text file, but with .mp3 extension
                mp3_filename = os.path.splitext(filename)[0] + '.mp3'
                output_path = os.path.join(audioFilePath, mp3_filename)
                
                # tts.save(output_path)
                synthesizeAudio(text, 'en-us', '', 'f', str(output_path))

                print(f"Generated voice-over for {filename} and saved as {mp3_filename}")

        print("Voice-over generation complete.")
        return audioFilePath
    
    except Exception as e:
        logging.error(e)
        return "ERROR_DURING_VOICE_OVER_GENERATION"
    

def synthesizeAudio(text, lang, voiceName, maleorFemale, outputFile):

    #"""Synthesizes speech from the input string of text."""
    from google.cloud import texttospeech

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'acquired-medley-416522-4a9996dad7ac.json'
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code=lang,
        # name=voiceName,
        ssml_gender=texttospeech.SsmlVoiceGender.MALE if maleorFemale == 'm' else texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open(outputFile, "wb") as out:
        out.write(response.audio_content)
        # print('Audio content written to file "output.mp3"')
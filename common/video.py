
from moviepy.editor import *
from pydub import AudioSegment
from pathlib import Path
import time
import logging


# generate the learning video for 2 or 3 mins 
def generateVideo(imageFilePath, audioFilePath, backgroundMusicPath, workingDir):

    try:

        # Define your paths
        png_dir = Path(imageFilePath)
        voiceover_dir = Path(audioFilePath)
        background_music_path = Path(backgroundMusicPath)
        output_dir = Path(workingDir)
        silent_audio_path = output_dir / 'silent_5sec.mp3'  # Will be generated

        # Ensure directories exist
        output_dir.mkdir(exist_ok=True)
        voiceover_dir.mkdir(exist_ok=True)

        # Generate a 5 sec silent audio file if it doesn't exist
        if not silent_audio_path.exists():
            silent_audio = AudioSegment.silent(duration=5000)  # Duration in milliseconds (5sec * 1000ms/sec)
            silent_audio.export(silent_audio_path, format="mp3")

        # Load background music and set its volume
        background_music = AudioFileClip(str(background_music_path)).volumex(0.03)

        # Note: In the revised step 3, when checking if a voice-over file exists,
        # if not, directly use `silent_audio_path` instead of checking for existence again.

        # Step 3: Generate intermediate videos efficiently
        intermediate_videos = []
        for png_path in sorted(png_dir.glob('*.png'), key=lambda x: int(x.stem)):
            voiceover_path = voiceover_dir / f"{png_path.stem}.mp3"
            if not voiceover_path.exists():
                voiceover_path = Path(silent_audio_path)  # Use the silent audio if the voice-over doesn't exist

            img_clip = ImageClip(str(png_path)).set_duration(AudioFileClip(str(voiceover_path)).duration)
            video_clip = img_clip.set_audio(AudioFileClip(str(voiceover_path)))
            intermediate_video_path = output_dir / f"{png_path.stem}.mp4"
            video_clip.write_videofile(str(intermediate_video_path), fps=1, codec='libx264', audio_codec='libmp3lame', preset='ultrafast')
            intermediate_videos.append(intermediate_video_path)

        # Step 4: Concatenate all intermediate videos
        final_clip_concat = concatenate_videoclips([VideoFileClip(str(video_path)) for video_path in intermediate_videos], method="compose")

        # Step 5: Add background music to the final video with lowered volume
        # The final_clip_concat has a defined duration here; we ensure the background music matches this duration
        if background_music.duration > final_clip_concat.duration:
            # If background music is longer, we cut it to match the video's duration
            background_music = background_music.subclip(0, final_clip_concat.duration)
        else:
            # If background music is shorter, loop it until it matches the video's duration
            loops_required = int(final_clip_concat.duration / background_music.duration) + 1
            background_music = concatenate_audioclips([background_music] * loops_required)
            background_music = background_music.subclip(0, final_clip_concat.duration)

        final_audio = CompositeAudioClip([final_clip_concat.audio, background_music])
        final_clip = final_clip_concat.set_audio(final_audio)


        # Explanation of Parameters for Compression:
        # codec="libx264": Uses the H.264 video codec for compression, which is widely supported and efficient.
        # audio_codec="libmp3lame": Specifies the use of the MP3 audio codec for the audio track.
        # bitrate="500k": Sets the target bitrate for the video, which directly affects file size and quality. You might need to adjust this value based on your quality requirements and the acceptable file size.
        # preset="fast": Affects the speed of compression. "fast" is a good middle ground, providing a balance between encoding speed and file size. Other options like "slower" can result in smaller files but take more time to encode.
        # ffmpeg_params=["-crf", "25", "-q:a", "5"]:
        # -crf "25": The Constant Rate Factor (CRF) value affects the video quality, with lower numbers meaning better quality and higher numbers increasing compression (at the cost of quality). The value of "25" is a suggestion; adjust between "23" and "28" for typical web video.
        # -q:a "5": Controls the quality of the MP3 audio compression, with lower numbers being higher quality. The scale for MP3 is usually from 0 to 9, where "5" represents a good balance between quality and file size.


        # Save the final video
        final_video_path = output_dir / "final_video_with_background_music.mp4"
        final_clip.write_videofile(str(final_video_path), codec='libx264', 
                                audio_codec='libmp3lame', 
                                preset='placebo', bitrate="500k",  ffmpeg_params=["-crf", "25", "-q:a", "5"])

        # A brief delay to ensure file handles are released by all processes
        time.sleep(10)

        return final_video_path
        # try:
        #     # Cleanup: Optionally remove intermediate videos
        #     for video_path in intermediate_videos:
        #         video_path.unlink()

        #     # Add any additional cleanup here
        #     # Cleanup temporary files created by moviepy/ffmpeg if necessary
        #     for temp_file in glob.glob("*.mpy"):
        #         os.remove(temp_file)
            
        #     print("Cleanup complete. Intermediate files deleted.")
        # except Exception as e:
        #     print(f"Error during cleanup: {e}")
    except Exception as e:
        logging.error("error in generateVideo method::" + str(e))
        return None

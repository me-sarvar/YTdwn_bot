import re
import os
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError  # Import the exception

def download_media(youtube_url, format):
    try:
        youtube = YouTube(youtube_url)
        if format == "mp3":
            audio_stream = youtube.streams.filter(only_audio=True, file_extension="mp4").first()
            audio_stream.download()
            new_filename = audio_stream.default_filename.replace(".mp4", ".mp3")
            os.rename(audio_stream.default_filename, new_filename)
            return new_filename
        elif format == "mp4":
            video_stream = youtube.streams.filter(file_extension="mp4").get_highest_resolution()
            video_stream.download()
            return video_stream.default_filename
        else:
            return None

    except AgeRestrictedError:
        return "age_restricted"  # Return this specific string to identify the error

    except Exception as e:  # Handle any other exception that might occur
        print(f"An unexpected error occurred: {e}")
        return None


def is_valid_youtube_url(url):
    return bool(re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+', url))

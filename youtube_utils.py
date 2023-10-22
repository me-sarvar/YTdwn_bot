import re
import os
from pytube import YouTube
from pytube.exceptions import AgeRestrictedError


def download_media(youtube_url, format):
    """
    Downloads media from a given YouTube URL in the specified format (mp3/mp4).

    :param youtube_url: The URL of the YouTube video to be downloaded.
    :param format: The desired format for the download ('mp3' or 'mp4').
    :return: The filename of the downloaded media or a specific error string.
    """
    try:
        youtube = YouTube(youtube_url)

        if format == "mp3":
            # Filter and get the first audio stream in mp4 format
            audio_stream = youtube.streams.filter(only_audio=True, file_extension="mp4").first()
            audio_stream.download()  # Download the audio stream

            # Rename the downloaded file from .mp4 to .mp3
            new_filename = audio_stream.default_filename.replace(".mp4", ".mp3")
            os.rename(audio_stream.default_filename, new_filename)

            return new_filename

        elif format == "mp4":
            # Filter and get the highest resolution video stream in mp4 format
            video_stream = youtube.streams.filter(file_extension="mp4").get_highest_resolution()
            video_stream.download()  # Download the video stream

            return video_stream.default_filename

        else:
            return None

    except AgeRestrictedError:
        # Return this specific string to identify age restricted content
        return "age_restricted"
    except Exception as e:
        # Handle any other exception that might occur
        print(f"An unexpected error occurred: {e}")
        return None


def is_valid_youtube_url(url):
    """
    Checks if the given URL is a valid YouTube URL.

    :param url: The URL to be checked.
    :return: True if valid, False otherwise.
    """
    # This regex matches both full YouTube URLs and shortened youtu.be URLs
    return bool(re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+', url))

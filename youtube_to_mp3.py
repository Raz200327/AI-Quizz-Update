import requests
from pytube import YouTube

class YouTubeMP3:
    def __init__(self, link):
        self.link = link
        self.youtube_link = YouTube(link)
        self.streams = self.youtube_link.streams.first()
        self.streams.download(output_path="./media")


    def get_audio_name(self):
        return self.youtube_link.title



from django.conf import settings
from googleapiclient.discovery import build


class YoutubeService:
    """Service to work with youtube api"""

    BASE_URL_PATTERN = r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})"

    def __init__(self, *args, **kwargs):
        self.client = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

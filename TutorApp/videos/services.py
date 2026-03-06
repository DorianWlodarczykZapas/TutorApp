import re
from datetime import timedelta

from django.conf import settings
from django.utils.translation import gettext as _
from googleapiclient.discovery import build
from videos.models import VideoTimestamp

HEADER_MAP = {
    "ĆWICZENIA": VideoTimestamp.TimestampType.EXERCISE,
    "ZADANIA": VideoTimestamp.TimestampType.TASK,
    "MATURA PODSTAWOWA": VideoTimestamp.TimestampType.LECTURE,
    "MATURA ROZSZERZONA": VideoTimestamp.TimestampType.LECTURE,
}


class YoutubeService:
    """Service to work with youtube api"""

    BASE_URL_PATTERN = r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})"

    def __init__(self, *args, **kwargs):
        self.client = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    def extract_video_id(self, url: str) -> str | None:
        """
        Extract video id from url

        Args:
        url (str): url to extract video id
        Returns:
        11 characters long video id
        """

        match = re.search(self.BASE_URL_PATTERN, url)
        return match.group(1) if match else None

    def extract_video_title_and_description(self, url: str) -> dict[str, str]:
        """Gets video title and description based on url and youtube api

        Args:
            url (str): url to extract video id
        Returns:
            Dictionary of video title and description
        """
        video_id = self.extract_video_id(url)

        if not video_id:
            raise ValueError("Invalid youtube url")

        response = self.client.videos().list(part="snippet", id=video_id).execute()

        if not response.get("items"):
            raise ValueError("Video not found")

        snippet = response["items"][0]["snippet"]

        return {
            "title": snippet["title"],
            "description": snippet["description"],
        }

    def parse_timestamps(self, text: str) -> list[dict]:
        """Parses youtube description text into list of timestamps

        Args:
            text (str): youtube description text

        Returns:
              list[dict]: List of dictonaries with keys 'label', 'start_time', 'timestamp_type'

        Raises:
            ValueError: If timestamps or text is valid
        """

        results = []

        current_type = None

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.upper() in HEADER_MAP:
                current_type = HEADER_MAP[line.upper()]
                continue

            match = re.match(r"(\d{2}:\d{2}:\d{2})\s*-?\s*(.+)", line)
            if match and current_type is not None:
                time_str, label = match.groups()
                h, m, s = map(int, time_str.split(":"))
                start_time = timedelta(hours=h, minutes=m, seconds=s)

                results.append(
                    {
                        "label": label.strip(),
                        "start_time": start_time,
                        "timestamp_type": current_type,
                    }
                )
        if not results:
            raise ValueError(_("No valid timestamps found"))

        return results

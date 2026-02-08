import re

from django import forms
from django.utils.translation import gettext_lazy as _
from videos.models import Video


class AddVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["title", "youtube_url", "section", "subject", "level"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "youtube_url": forms.URLInput(attrs={"class": "form-control"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "level": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_youtube_url(self):

        url = self.cleaned_data.get("youtube_url")

        patterns = [
            r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        ]

        video_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break

        if not video_id:
            raise forms.ValidationError(
                _("Invalid YouTube URL. Please provide a valid YouTube video link.")
            )

        normalized_url = f"https://www.youtube.com/watch?v={video_id}"
        return normalized_url

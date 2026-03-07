import re

from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from videos.models import Video
from videos.services import YoutubeService


class AddVideoForm(forms.ModelForm):
    timestamps_text = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 10}),
        required=False,
        label=_("Timestamps"),
        help_text=_("Paste YouTube description with timestamps here"),
    )

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

        service = YouTubeService()
        video_id = service.extract_video_id(url)

        if not video_id:
            raise forms.ValidationError(
                _("Invalid YouTube URL. Please provide a valid YouTube video link.")
            )

        return f"https://www.youtube.com/watch?v={video_id}"

class VideoFilterForm(forms.Form):
    title = forms.ModelChoiceField(
        queryset=Video.objects.all(),
        widget=ModelSelect2Widget(
            model=Video,
            search_fields=["title__icontains"],
        ),
        required=False,
        label=_("Search videos"),
    )

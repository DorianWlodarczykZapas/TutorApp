from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Video, VideoTimestamp


class AddVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            "title",
            "level",
            "youtube_url",
            "section",
            "subject",
        ]
        labels = {
            "title": _("Title"),
            "level": _("Education level"),
            "youtube_url": _("YouTube link"),
            "section": _("Book section"),
            "subject": _("Subject"),
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": _("Topic title from the book")}
            ),
            "youtube_url": forms.URLInput(
                attrs={"placeholder": _("https://youtube.com/...")}
            ),
            "section": forms.Select(),
            "subject": forms.Select(),
            "level": forms.Select(),
        }


class VideoTimestampForm(forms.ModelForm):
    class Meta:
        model = VideoTimestamp
        fields = ["label", "start_time", "timestamp_type"]
        labels = {
            "label": _("Label"),
            "start_time": _("Start time"),
            "timestamp_type": _("Type"),
        }
        widgets = {
            "start_time": forms.TimeInput(
                format="%H:%M:%S",
                attrs={"placeholder": "HH:MM:SS"},
            ),
        }


TimestampFormSet = inlineformset_factory(
    Video,
    VideoTimestamp,
    form=VideoTimestampForm,
    extra=1,
    can_delete=True,
)

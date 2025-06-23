from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Video


class AddVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            "title",
            "level",
            "youtube_url",
            "type",
            "subcategory",
        ]
        labels = {
            "title": _("Title"),
            "level": _("Education level"),
            "youtube_url": _("YouTube link"),
            "type": _("Book section"),
            "subcategory": _("Subcategory"),
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": _("Topic title from the book")}
            ),
            "youtube_url": forms.URLInput(
                attrs={"placeholder": _("https://youtube.com/...")}
            ),
            "type": forms.Select(choices=Video.section),
            "subcategory": forms.TextInput(
                attrs={"placeholder": _("e.g. operations on fractions")}
            ),
            "level": forms.Select(choices=Video.VideoLevel.choices),
        }

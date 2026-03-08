from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from videos.models import Video


class AddVideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ["youtube_url", "section", "subject", "level"]
        widgets = {
            "youtube_url": forms.URLInput(attrs={"class": "form-control"}),
            "section": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "level": forms.Select(attrs={"class": "form-select"}),
        }


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

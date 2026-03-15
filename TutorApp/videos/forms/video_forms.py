from common.forms import TypedChoiceMixin
from courses.choices import SchoolLevelChoices, SubjectChoices
from courses.models import Section
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from videos.models import Video


class AddVideoForm(TypedChoiceMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"] = self._make_typed_choice(SubjectChoices, _("Subject"))
        self.fields["level"] = self._make_typed_choice(
            SchoolLevelChoices, _("School Level")
        )

    class Meta:
        model = Video
        fields = ["youtube_url", "section", "subject", "level"]
        labels = {
            "youtube_url": _("YouTube URL"),
            "section": _("Section"),
        }
        widgets = {
            "youtube_url": forms.URLInput(attrs={"placeholder": " "}),
            "section": ModelSelect2Widget(
                model=Section,
                search_fields=["name__icontains"],
                attrs={"placeholder": " "},
            ),
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

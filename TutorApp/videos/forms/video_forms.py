from core.forms import TypedChoiceMixin
from courses.choices import SchoolLevelChoices, SubjectChoices
from courses.models import Section
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from videos.models import Video, VideoTimestamp


class AddVideoStep1Form(TypedChoiceMixin, forms.Form):
    youtube_url = forms.URLField(
        label=_("YouTube URL"),
        widget=forms.URLInput(attrs={"placeholder": " "}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"] = self._make_typed_choice(SubjectChoices, _("Subject"))
        self.fields["level"] = self._make_typed_choice(
            SchoolLevelChoices, _("School Level")
        )
        self.fields["section"] = forms.ModelChoiceField(
            queryset=Section.objects.all(),
            label=_("Section"),
            widget=ModelSelect2Widget(
                model=Section,
                search_fields=["name__icontains"],
                attrs={
                    "placeholder": " ",
                    "data-placeholder": _("Section"),
                },
            ),
            empty_label=_("Section"),
        )


class AddVideoStep2Form(forms.Form):
    title = forms.CharField(
        label=_("Title"),
        widget=forms.Textarea(attrs={"placeholder": " "}),
    )


class TimestampForm(forms.Form):
    label = forms.CharField(
        label=_("Label"),
        widget=forms.TextInput(attrs={"placeholder": " "}),
    )
    start_time = forms.CharField(
        label=_("Start time"),
        widget=forms.TextInput(attrs={"placeholder": " "}),
    )
    timestamp_type = forms.TypedChoiceField(
        choices=VideoTimestamp.TimestampType.choices,
        coerce=int,
        label=_("Type"),
        widget=forms.Select(attrs={"placeholder": " "}),
    )


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

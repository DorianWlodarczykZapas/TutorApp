import django_filters
from courses.choices import SubjectChoices
from courses.models import Section
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from .models import Video


class VideoFilterSet(django_filters.FilterSet):

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label=_("Title"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search by title"),
            }
        ),
    )

    section = django_filters.ModelChoiceFilter(
        queryset=Section.objects.all(),
        label=_("Section"),
        empty_label=_("All Sections"),
        widget=ModelSelect2Widget(
            model=Section,
            search_fields=["name__icontains"],
            attrs={
                "data-placeholder": _("Search Section"),
                "data-allow-clear": "true",
                "class": "form-control",
            },
        ),
    )

    subject = django_filters.ChoiceFilter(
        field_name="section__subject",
        choices=SubjectChoices.choices,
        label=_("Subject"),
        empty_label=_("Choose Subject"),
    )

    class Meta:
        model = Video
        fields = ["title", "section", "subject"]

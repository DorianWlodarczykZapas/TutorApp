from typing import Any, Dict

import django_filters
from courses.models import Section
from django import forms
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from .models import Video


class VideoFilterSet(django_filters.FilterSet):
    """
    Filter set for the Video model with automatic string cleaning.
    """

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label=_("Title"),
        method="filter_strip_title",
    )

    section = django_filters.ModelChoiceFilter(
        queryset=Section.objects.all(), label=_("Section")
    )

    subject = django_filters.ChoiceFilter(
        choices=Video.SubjectChoices.choices, label=_("Subject")
    )

    level = django_filters.ChoiceFilter(
        choices=Video.LevelChoices.choices, label=_("Level")
    )

    class Meta:
        model = Video
        fields = ["title", "section", "subject", "level"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes filters and injects CSS classes for Select2
        """
        super().__init__(*args, **kwargs)

        select2_attrs: Dict[str, str] = {
            "class": "form-control select2-init",
            "style": "width: 100%",
        }

        if "section" in self.filters:
            self.filters["section"].field.widget = forms.Select(attrs=select2_attrs)

        if "subject" in self.filters:
            self.filters["subject"].field.widget = forms.Select(attrs=select2_attrs)

        if "level" in self.filters:
            self.filters["level"].field.widget = forms.Select(attrs=select2_attrs)

    def filter_strip_title(
        self, queryset: QuerySet[Video], name: str, value: str
    ) -> QuerySet[Video]:
        """
        Cleans the filter value of whitespace before executing the query.

        Args:
            queryset: The base QuerySet of Video models.
            name: The field name (title).
            value: The value provided by the user.

        Returns:
            QuerySet: The filtered dataset.
        """
        if value:
            stripped_value: str = value.strip()
            lookup: str = f"{name}__icontains"
            return queryset.filter(**{lookup: stripped_value})

        return queryset

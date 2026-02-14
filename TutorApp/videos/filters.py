from typing import Any

import django_filters
from courses.models import Section
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

    def filter_strip_title(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
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

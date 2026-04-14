import django_filters
from courses.choices import SubjectChoices
from courses.models import Section
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget, Select2Widget
from quizes.models import Quiz


class QuizFilterSet(django_filters.FilterSet):

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label=_("Title"),
        method="filter_strip_title",
    )

    section = django_filters.ModelChoiceFilter(
        queryset=Section.objects.all(),
        label=_("Section"),
        empty_label=_("All Sections"),
        widget=ModelSelect2Widget(
            model=Section,
            search_fields=["name__icontains"],
            attrs={
                "data-placeholder": _("Select section..."),
                "data-allow-clear": "true",
                "class": "form-control",
            },
        ),
    )

    subject = django_filters.ChoiceFilter(
        field_name="section__subject",
        choices=SubjectChoices.choices,
        label=_("Subject"),
        empty_label=_("All Subjects"),
        widget=Select2Widget(
            attrs={
                "data-placeholder": _("Select subject..."),
                "data-allow-clear": "true",
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Quiz
        fields = ["title", "section"]

    def filter_strip_title(
        self, queryset: QuerySet[Quiz], name: str, value: str
    ) -> QuerySet[Quiz]:
        if value:
            stripped_value: str = value.strip()
            lookup: str = f"{name}__icontains"
            return queryset.filter(**{lookup: stripped_value})

        return queryset

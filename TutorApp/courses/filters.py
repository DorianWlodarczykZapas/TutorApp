import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget

from .models import Section, TrainingTask


def filter_section(request):
    if request is None:
        return Section.objects.none()
    return Section.objects.all().order_by("name")


class TrainingTaskFilter(django_filters.FilterSet):
    """
    Filterclass to let user filter training tasks by:
    - grade by default
    - search task content
    - choose level type
    - search section
    """

    search = django_filters.CharFilter(
        field_name="task_content",
        lookup_expr="icontains",
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "style": "resize: none;",
            }
        ),
    )

    section = django_filters.ModelChoiceFilter(
        queryset=filter_section,
        label=_("Section"),
        empty_label=_("All sections"),
        widget=ModelSelect2Widget(
            model=Section,
            search_fields=["name__icontains"],
            attrs={"class": "field-search-single"},
        ),
    )

    level = django_filters.MultipleChoiceFilter(
        choices=TrainingTask._meta.get_field("level").choices,
        widget=forms.CheckboxSelectMultiple(),
    )

    completed = django_filters.ChoiceFilter(
        method="filter_completed",
        label=_("Status"),
        choices=[
            ("", _("All tasks")),
            ("completed", _("Completed")),
            ("uncompleted", _("Not completed")),
        ],
        empty_label=None,
        widget=forms.Select(attrs={"class": "filter-select"}),
    )

    class Meta:
        model = TrainingTask
        fields = []

    @property
    def qs(self):
        queryset = super().qs
        user = self.request.user

        if not user.grade:
            return queryset

        if self.data.get("section"):
            return queryset

        return queryset.filter(section__grade=user.grade)

    def filter_completed(self, queryset, name, value):
        user = self.request.user
        if value == "completed":
            return queryset.filter(usertaskcompletion__user=user)
        elif value == "uncompleted":
            return queryset.exclude(usertaskcompletion__user=user)
        return queryset

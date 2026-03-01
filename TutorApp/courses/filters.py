import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Book, Section, TrainingTask


class TrainingTaskFilter(django_filters.FilterSet):
    """
    FilterSet for TrainingTask model

    Filters:
    - section: By section (dropdown)
    - level: By difficulty level (checkboxes)
    - book: By book (dropdown)
    - completed: Show only completed/uncompleted tasks
    - search: Search in task_content
    """

    search = django_filters.CharFilter(
        field_name="task_content",
        lookup_expr="icontains",
        label=_("Search in task"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Search..."),
            }
        ),
    )

    book = django_filters.ModelChoiceFilter(
        queryset=Book.objects.all(),
        field_name="section__book",
        label=_("Book"),
        empty_label=_("All books"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    section = django_filters.ModelChoiceFilter(
        queryset=Section.objects.all().select_related("book"),
        label=_("Section"),
        empty_label=_("All sections"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    level = django_filters.MultipleChoiceFilter(
        choices=TrainingTask._meta.get_field("level").choices,
        label=_("Difficulty Level"),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
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
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = TrainingTask
        fields = ["search", "book", "section", "level", "completed"]

    def __init__(self, *args, user=None, **kwargs):
        """ """
        super().__init__(*args, **kwargs)
        self.user = user

        if user and user.grade:

            self.filters["book"].queryset = Book.objects.filter(
                grade_level=user.grade
            ).order_by("title")

            self.filters["section"].queryset = (
                Section.objects.filter(book__grade_level=user.grade)
                .select_related("book")
                .order_by("book__title", "name")
            )

    def filter_completed(self, queryset, name, value):
        """ """
        if not self.user:
            return queryset

        if value == "completed":

            return queryset.filter(completed_by=self.user)
        elif value == "uncompleted":

            return queryset.exclude(completed_by=self.user)

        return queryset

    @property
    def qs(self):
        """ """
        queryset = super().qs

        if self.user and self.user.grade and not self.data:
            queryset = queryset.filter(section__book__grade_level=self.user.grade)

        return queryset.select_related("section", "section__book").prefetch_related(
            "completed_by"
        )

import django_filters
from courses.models import Book, Section, Topic, TrainingTask
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Exam, ExamTask

SCHOOL_PRIMARY = 1
SCHOOL_SECONDARY = 2

EXAM_TYPE_MATRICULATION = 1
EXAM_TYPE_EIGHTH_GRADE = 2

SCHOOL_TO_EXAM_TYPE = {
    SCHOOL_PRIMARY: EXAM_TYPE_EIGHTH_GRADE,
    SCHOOL_SECONDARY: EXAM_TYPE_MATRICULATION,
}


class ExamTaskFilter(django_filters.FilterSet):
    section = django_filters.ModelChoiceFilter(
        field_name="section",
        queryset=Section.objects.none(),
        label="Section",
        empty_label="All",
        required=False,
    )

    topic = django_filters.ModelChoiceFilter(
        field_name="topic",
        queryset=Topic.objects.none(),
        label="Topic",
        empty_label="All",
        required=False,
    )

    level_type = django_filters.ChoiceFilter(
        field_name="exam__level_type",
        choices=Exam._meta.get_field("level_type").choices,
        label="Level",
        required=False,
    )

    completed_by = django_filters.BooleanFilter(
        method="filter_completed",
        label="Completed",
        required=False,
        widget=django_filters.widgets.BooleanWidget(),
    )

    class Meta:

        model = ExamTask
        fields = ["section", "topic", "level_type", "completed_by"]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        user = getattr(request, "user", None)
        school_type = getattr(user, "school_type", None)

        if school_type:
            if "section" in self.filters:
                self.filters["section"].queryset = Section.objects.filter(
                    school_type=school_type
                ).order_by("id")
            if "topic" in self.filters:
                self.filters["topic"].queryset = Topic.objects.filter(
                    school_type=school_type
                ).order_by("id")

        if school_type == SCHOOL_PRIMARY:
            self.filters.pop("level_type", None)

    def filter_completed(self, queryset, name, value):

        if value is None:
            return queryset
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:

            return queryset.none() if value else queryset
        if value:
            return queryset.filter(completed_by=user)
        return queryset.exclude(completed_by=user)


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

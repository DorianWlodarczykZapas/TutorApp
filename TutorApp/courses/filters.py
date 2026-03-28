import django_filters
from django.utils.translation import gettext_lazy as _

from .models import Section, TrainingTask


def filter_section(request):

    if request is None:
        return Section.objects.none()
    else:
        user = request.user
        return Section.objects.filter(grade=user.grade)


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
    )

    section = django_filters.ModelChoiceFilter(queryset=filter_section)

    level = django_filters.MultipleChoiceFilter(
        choices=TrainingTask._meta.get_field("level").choices,
    )

    completed = django_filters.ChoiceFilter(
        method="filter_completed",
        choices=[
            ("", _("All tasks")),
            ("completed", _("Completed")),
            ("uncompleted", _("Not completed")),
        ],
        empty_label=None,
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

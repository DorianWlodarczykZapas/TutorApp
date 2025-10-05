import django_filters
from django import forms
from .models import ExamTask, Exam, Section, Topic


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
        field_name='section',
        queryset=Section.objects.none(),
        label='Section',
        empty_label='All',
        required=False,
    )

    topic = django_filters.ModelChoiceFilter(
        field_name='topic',
        queryset=Topic.objects.none(),
        label='Topic',
        empty_label='All',
        required=False,
    )

    level_type = django_filters.ChoiceFilter(
        field_name='exam__level_type',
        choices=Exam._meta.get_field('level_type').choices,
        label='Level',
        required=False,
    )


    completed_by = django_filters.BooleanFilter(
        method='filter_completed',
        label='Completed',
        required=False,
        widget=django_filters.widgets.BooleanWidget(),
    )

    class Meta:
        model = ExamTask
        fields = ['section', 'topic', 'level_type', 'completed_by']

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        user = getattr(request, 'user', None)
        school_type = getattr(user, 'school_type', None)


        if school_type:
            if 'section' in self.filters:
                self.filters['section'].queryset = Section.objects.filter(
                    school_type=school_type
                ).order_by('id')
            if 'topic' in self.filters:
                self.filters['topic'].queryset = Topic.objects.filter(
                    school_type=school_type
                ).order_by('id')


        if school_type == SCHOOL_PRIMARY:
            self.filters.pop('level_type', None)

    def filter_completed(self, queryset, name, value):

        if value is None:
            return queryset
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:

            return queryset.none() if value else queryset
        if value:
            return queryset.filter(completed_by=user)
        return queryset.exclude(completed_by=user)
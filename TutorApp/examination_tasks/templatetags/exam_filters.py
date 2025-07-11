from django import template

from ..models import MONTH_CHOICES, Exam

register = template.Library()


@register.filter
def get_month_display(month_number):
    return dict(MONTH_CHOICES).get(int(month_number), month_number)


@register.filter
def get_level_display(level_number):
    return dict(Exam.LEVEL_CHOICES).get(int(level_number), level_number)


@register.filter
def get_category_display(category_number):
    from ..models import MathMatriculationTasks

    return dict(MathMatriculationTasks._meta.get_field("category").choices).get(
        int(category_number), category_number
    )

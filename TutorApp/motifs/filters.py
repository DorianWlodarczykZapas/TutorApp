import django_filters
from models import Motif

class MotifFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Search in content'
    )

    class Meta:
        model = Motif
        fields = {
            'subject': ['exact'],
            'section': ['exact'],
            'level_type': ['exact'],

        }
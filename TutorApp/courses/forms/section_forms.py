from courses.models import Book, Section
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2MultipleWidget


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["books", "name"]
        labels = {
            "books": _("Books"),
            "name": _("Section Name"),
        }
        widgets = {
            "books": ModelSelect2MultipleWidget(
                model=Book,
                search_fields=["title__icontains"],
                attrs={
                    "placeholder": _("Search for a book..."),
                    "data-ajax--url": "/select2/fields/auto.json",
                },
            )
        }

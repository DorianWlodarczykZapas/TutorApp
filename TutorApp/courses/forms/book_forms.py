from courses.models import Book
from django import forms
from django.utils.translation import gettext_lazy as _


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "publication_year",
            "school_level",
        ]
        labels = {
            "title": _("Book Title"),
            "author": _("Author"),
            "publication_year": _("Publication Year"),
            "school_level": _("School Level"),
        }

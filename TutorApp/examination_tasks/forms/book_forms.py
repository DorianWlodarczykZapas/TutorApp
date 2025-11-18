from django.forms import forms
from django.utils.translation import gettext_lazy as _

from ..models import Book


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

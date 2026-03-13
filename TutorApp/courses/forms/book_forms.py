from common.forms import TypedChoiceMixin
from courses.choices import (
    BookTypeChoices,
    GradeChoices,
    SchoolLevelChoices,
    SubjectChoices,
)
from courses.models import Book
from django import forms
from django.utils.translation import gettext_lazy as _


class BookForm(TypedChoiceMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["book_type"] = self._make_typed_choice(
            BookTypeChoices, _("Book Type")
        )

        self.fields["school_level"] = self._make_typed_choice(
            SchoolLevelChoices, _("School Level")
        )

        self.fields["subject"] = self._make_typed_choice(SubjectChoices, _("Subject"))

        self.fields["grade"] = self._make_typed_choice(GradeChoices, _("Grade"))

    class Meta:
        model = Book
        fields = [
            "title",
            "book_type",
            "authors",
            "publication_year",
            "school_level",
            "subject",
            "grade",
        ]
        labels = {
            "title": _("Book Title"),
            "authors": _("Authors"),
            "publication_year": _("Publication Year"),
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": " "}),
            "authors": forms.TextInput(attrs={"placeholder": " "}),
            "publication_year": forms.NumberInput(attrs={"placeholder": " "}),
        }

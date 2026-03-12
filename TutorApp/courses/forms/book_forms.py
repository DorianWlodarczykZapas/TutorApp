from courses.models import Book
from django import forms
from django.utils.translation import gettext_lazy as _
from examination_tasks import choices


class BookForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        school_level_choices = [("", _("School Level"))] + list(
            choices.SchoolLevelChoices.choices
        )
        subject_choices = [("", _("Subject"))] + list(choices.SubjectChoices.choices)
        grade_choices = [("", _("Grade"))] + list(choices.GradeChoices.choices)
        book_type_choices = [("", _("Book Type"))] + list(
            choices.BookTypeChoices.choices
        )

        self.fields["book_type"] = forms.TypedChoiceField(
            choices=book_type_choices,
            widget=forms.Select(attrs={"placeholder": " "}),
            label=_("Book Type"),
            coerce=int,
            empty_value=None,
        )

        self.fields["school_level"] = forms.TypedChoiceField(
            choices=school_level_choices,
            widget=forms.Select(attrs={"placeholder": " "}),
            label=_("School Level"),
            coerce=int,
            empty_value=None,
        )
        self.fields["subject"] = forms.TypedChoiceField(
            choices=subject_choices,
            widget=forms.Select(attrs={"placeholder": " "}),
            label=_("Subject"),
            coerce=int,
            empty_value=None,
        )
        self.fields["grade"] = forms.TypedChoiceField(
            choices=grade_choices,
            widget=forms.Select(attrs={"placeholder": " "}),
            label=_("Grade"),
            coerce=int,
            empty_value=None,
            required=False,
        )

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

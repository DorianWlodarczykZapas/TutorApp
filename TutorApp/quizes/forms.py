from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import Answer, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            "type",
            "question",
            "question_picture",
            "explanation",
            "explanation_picture",
        ]
        labels = {
            "type": _("Section"),
            "question": _("Question"),
            "question_picture": _("Question image"),
            "explanation": _("Explanation"),
            "explanation_picture": _("Explanation image"),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text", "is_correct"]
        labels = {
            "text": _("Answer"),
            "is_correct": _("Correct?"),
        }


class BaseAnswerFormSet(BaseInlineFormSet):
    """
    Custom base class for answer formset.
    Adds validation that checks that exactly one
    response is marked as valid.
    """

    def clean(self):
        super().clean()

        if not any(self.errors):
            correct_answers_count = 0
            for form in self.forms:

                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    if form.cleaned_data.get("is_correct", False):
                        correct_answers_count += 1

            if correct_answers_count == 0:
                raise forms.ValidationError(
                    _("You must mark at least one answer as correct."),
                    code="no_correct_answer",
                )


AnswerFormSet = inlineformset_factory(
    Quiz,
    Answer,
    form=AnswerForm,
    formset=BaseAnswerFormSet,
    extra=4,
    can_delete=False,
    min_num=2,
    validate_min=True,
)


class CategorySelectForm(forms.Form):
    category = forms.ChoiceField(
        choices=Quiz.section,
        label=_("Choose a category"),
        widget=forms.Select(
            attrs={
                "class": "form-select select2",
                "data-placeholder": _("Start typing to search category"),
            }
        ),
    )

from django import forms
from django.db import models


class TypedChoiceMixin:

    def _make_typed_choice(
        self,
        choice_cls: type[models.Choices] | list | tuple,
        label: str,
        required: bool = True,
    ) -> forms.TypedChoiceField:

        if isinstance(choice_cls, type) and issubclass(choice_cls, models.Choices):
            actual_choices = choice_cls.choices
        else:

            actual_choices = choice_cls

        return forms.TypedChoiceField(
            choices=[("", label)] + list(actual_choices),
            widget=forms.Select(
                attrs={
                    "placeholder": "",
                    "class": "form-input",
                }
            ),
            coerce=int,
            empty_value=None,
            required=required,
        )

from django import forms


class TypedChoiceMixin:
    def _make_typed_choice(self, choice_cls, label, required=True):
        return forms.TypedChoiceField(
            choices=[("", label)] + list(choice_cls.choices),
            widget=forms.Select(attrs={"placeholder": ""}),
            coerce=int,
            empty_value=None,
            required=required,
        )

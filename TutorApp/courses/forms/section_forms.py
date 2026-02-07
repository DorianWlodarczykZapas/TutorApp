from courses.models import Section
from django.forms import forms
from django.utils.translation import gettext_lazy as _


class SectionForm(forms.Form):
    class Meta:
        model = Section
        fields = ["book", "name"]
        labels = {
            "book": _("Book Title"),
            "name": _("Section Name"),
        }

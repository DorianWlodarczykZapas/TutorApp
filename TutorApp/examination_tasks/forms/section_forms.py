from django.forms import forms
from django.utils.translation import gettext_lazy as _

from ..models import Section


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["book", "name"]
        labels = {
            "book": _("Book Title"),
            "name": _("Section Name"),
        }

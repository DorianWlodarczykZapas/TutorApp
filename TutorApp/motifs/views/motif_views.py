from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.mixins import TeacherRequiredMixin

from ..forms.motif_forms import AddMotifForm
from ..models import Motif


class AddMotifView(TeacherRequiredMixin, CreateView):
    model = Motif
    form_class = AddMotifForm
    template_name = "motifs/add_motif.html"
    success_url = reverse_lazy("motifs:add_motif")

    def form_valid(self, form: AddMotifForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, _("Successfully added motif"))

        return response

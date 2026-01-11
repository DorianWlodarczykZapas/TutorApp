from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from users.mixins import TeacherRequiredMixin
from django_filters.views import FilterView
from ..forms.motif_forms import AddMotifForm
from ..models import Motif
from ..filters import MotifFilter
from django.views.generic import DeleteView

class AddMotifView(TeacherRequiredMixin, CreateView):
    model = Motif
    form_class = AddMotifForm
    template_name = "motifs/add_motif.html"
    success_url = reverse_lazy("motifs:add_motif")

    def form_valid(self, form: AddMotifForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, _("Successfully added motif"))

        return response


class MotifListView(LoginRequiredMixin, FilterView):
    model = Motif
    template_name = "motifs/motif_list.html"
    filterset_class = MotifFilter
    paginate_by = 10

class MotifDeleteView(TeacherRequiredMixin, DeleteView):
    model = Motif
    success_url = reverse_lazy("motifs:list_motifs")




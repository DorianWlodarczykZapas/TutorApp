from typing import Any, Dict

from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Exam
from .forms import ExamForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        user = self.request.user
        return bool(user.is_active and user.is_staff)

class ExamCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'examination_tasks/exam_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = _('Add New Exam')
        return data

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(self.request, _('Exam added successfully!'))

        return HttpResponseRedirect(reverse_lazy('examination_tasks:exam_add'))

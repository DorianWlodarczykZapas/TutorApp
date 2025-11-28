from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView


class SolveQuizWizard(LoginRequiredMixin, SessionWizardView):
    template_name = "quizes/quiz_solve_wizard.html"

    def get_form_list(self):
        pass

    def done(self, form_list, **kwargs) -> HttpResponse:
        pass

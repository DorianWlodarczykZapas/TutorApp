from django.contrib.auth.middleware import LoginRequiredMiddleware
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView


class SolveQuizWizard(LoginRequiredMiddleware, SessionWizardView):
    template_name = "quizes/quiz_solve_wizard.html"

    def get_form_list(self):
        pass

    def done(self, form_list, **kwargs) -> HttpResponse:
        pass

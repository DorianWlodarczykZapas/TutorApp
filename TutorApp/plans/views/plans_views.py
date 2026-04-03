from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from plans.models import Plan


class PlansListView(LoginRequiredMixin, ListView):
    model = Plan
    template_name = "plans/plans_list.html"
    context_object_name = "plans"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_plan = user.userplan
        context["user_plan"] = user_plan
        context["current_plan"] = user_plan.plan.name
        context["valid_to"] = user_plan.valid_to
        return context

import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView
from plans.models import Plan, UserPlan
from plans.services import StripeService


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


class ProcessPaymentView(LoginRequiredMixin, View):
    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        user_plan = get_object_or_404(UserPlan, user=self.request.user)
        stripe_service = StripeService(user_plan=user_plan)
        try:

            result = stripe_service.process_payment(plan=plan)

            if plan.type == Plan.PlanType.ULTIMATE:
                return JsonResponse({"client_secret": result.client_secret})
            else:
                return JsonResponse({"subscription_id": result.id})
        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)

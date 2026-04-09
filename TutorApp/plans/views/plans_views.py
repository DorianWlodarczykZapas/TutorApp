import json

import stripe
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from plans.models import Plan, UserPlan
from plans.services import PlanService, StripeService


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

    def get_queryset(self) -> QuerySet:
        user_plan = self.request.user.userplan
        return PlanService(user_plan).get_available_plans()


class CardProcessPaymentView(LoginRequiredMixin, View):
    def get(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        return render(
            request,
            "plans/card_payment.html",
            {"plan": plan, "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY},
        )

    def post(self, request, plan_id):

        data = json.loads(request.body)
        payment_method_id = data.get("payment_method_id")
        plan = get_object_or_404(Plan, id=plan_id)
        user_plan = get_object_or_404(UserPlan, user=self.request.user)
        stripe_service = StripeService(user_plan=user_plan)

        try:
            result = stripe_service.process_payment(
                plan=plan,
                payment_type="card",
                payment_method_id=payment_method_id,
            )

            if plan.type == Plan.PlanType.ULTIMATE:
                return JsonResponse({"client_secret": result.client_secret})
            else:
                return JsonResponse({"subscription_id": result.id})
        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)


class BlikProcessPaymentView(LoginRequiredMixin, View):
    def get(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        return render(
            request,
            "plans/blik_payment.html",
            {"plan": plan, "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY},
        )

    def post(self, request, plan_id):
        data = json.loads(request.body)
        payment_method_id = data.get("payment_method_id")
        blik_code = data.get("blik_code")
        plan = get_object_or_404(Plan, id=plan_id)
        user_plan = get_object_or_404(UserPlan, user=self.request.user)
        stripe_service = StripeService(user_plan=user_plan)

        try:

            result = stripe_service.process_payment(
                plan=plan,
                payment_method_id=payment_method_id,
                payment_type="blik",
                blik_code=blik_code,
            )

            if plan.type == Plan.PlanType.ULTIMATE:
                return JsonResponse({"client_secret": result.client_secret})
            else:
                return JsonResponse({"subscription_id": result.id})
        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)


class ConfirmPlanView(LoginRequiredMixin, View):
    def get(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id)
        return render(
            request,
            "plans/confirm_plan.html",
            {"plan": plan, "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY},
        )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            customer_id = payment_intent.customer
            try:
                user_plan = UserPlan.objects.get(stripe_customer_id=customer_id)
            except UserPlan.DoesNotExist:
                return HttpResponse(status=400)

            PlanService(user_plan=user_plan).activate_ultimate()

        elif event.type == "customer.subscription.updated":
            subscription = event.data.object
            customer_id = subscription.customer
            try:
                user_plan = UserPlan.objects.get(stripe_customer_id=customer_id)
            except UserPlan.DoesNotExist:
                return HttpResponse(status=400)
            PlanService(user_plan=user_plan).activate_premium()

        return HttpResponse(status=200)

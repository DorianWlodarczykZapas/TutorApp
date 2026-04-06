from django.urls import path
from plans.views.plans_views import (
    BlikProcessPaymentView,
    CardProcessPaymentView,
    ConfirmPlanView,
    PlansListView,
    StripeWebhookView,
)

app_name = "plans"

urlpatterns = [
    path("", PlansListView.as_view(), name="plans"),
    path("confirm/<plan_id>/", ConfirmPlanView.as_view(), name="confirm_payment"),
    path(
        "payment/card/<plan_id>/",
        CardProcessPaymentView.as_view(),
        name="card_payment_process",
    ),
    path(
        "payment/blik/<plan_id>/",
        BlikProcessPaymentView.as_view(),
        name="blik_payment_process",
    ),
    path("webhook/", StripeWebhookView.as_view(), name="webhook"),
]

from django.urls import path
from plans.views.plans_views import PlansListView, ProcessPaymentView, StripeWebhookView

app_name = "plans"

urlpatterns = [
    path("", PlansListView.as_view(), name="plans"),
    path("payment/<int:plan_id>/", ProcessPaymentView.as_view(), name="payment"),
    path("webhook/", StripeWebhookView.as_view(), name="webhook"),
]

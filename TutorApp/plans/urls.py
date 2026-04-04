from django.urls import path
from plans.views.plans_views import PlansListView, ProcessPaymentView

app_name = "plans"

urlpatterns = [
    path("", PlansListView.as_view(), name="plans"),
    path("payment/<int:plan_id>/", ProcessPaymentView.as_view(), name="payment"),
]

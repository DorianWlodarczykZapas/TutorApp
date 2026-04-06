from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

import stripe
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils import timezone
from plans.models import Plan, UserPlan


class PlanService:
    def __init__(self, user_plan: UserPlan):
        self.user_plan = user_plan

    def downgrade_if_expired(self) -> bool:
        today = timezone.now().date()

        if self.user_plan.is_trial and today > self.user_plan.valid_to:
            base_plan = Plan.objects.filter(type=Plan.PlanType.BASE).first()

            if base_plan:
                self.user_plan.plan = base_plan
                self.user_plan.is_trial = False
                self.user_plan.save()
                return True
            return False
        return False

    def activate_ultimate(self) -> None:
        ultimate_plan = Plan.objects.get(type=Plan.PlanType.ULTIMATE)
        self.user_plan.plan = ultimate_plan
        self.user_plan.valid_to = None
        self.user_plan.is_active = True

        self.user_plan.last_payment_date = date.today()
        self.user_plan.save()

    def activate_premium(self) -> None:
        premium_plan = Plan.objects.get(type=Plan.PlanType.PREMIUM)
        today = date.today()
        self.user_plan.plan = premium_plan
        self.user_plan.valid_to = today + relativedelta(months=1)
        self.user_plan.is_active = True
        self.user_plan.last_payment_date = today
        self.user_plan.next_payment_date = today + relativedelta(months=1)
        self.user_plan.save()


class PaymentStrategy(ABC):

    @abstractmethod
    def process(self, plan: Plan, payment_method_id: str, **kwargs):
        pass


class CardPaymentStrategy(PaymentStrategy):
    def __init__(self, stripe_service: "StripeService"):
        self.stripe_service = stripe_service

    def process(self, plan: Plan, payment_method_id: str, **kwargs):
        if plan.type == Plan.PlanType.ULTIMATE:
            return self.stripe_service.create_payment_intent(plan, payment_method_id)
        else:
            return self.stripe_service.create_subscription(plan, payment_method_id)


class BlikPaymentStrategy(PaymentStrategy):
    def __init__(self, stripe_service: "StripeService"):
        self.stripe_service = stripe_service

    def process(self, plan: Plan, payment_method_id: str, **kwargs):
        blik_code = kwargs.get("blik_code")
        return self.stripe_service.create_blik_payment_intent(plan, blik_code)


class StripeService:
    def __init__(self, user_plan: UserPlan):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.user_plan = user_plan

    def get_or_create_customer(self) -> str:
        if self.user_plan.stripe_customer_id:
            return self.user_plan.stripe_customer_id
        customer = stripe.Customer.create(
            email=self.user_plan.user.email,
            name=self.user_plan.user.username,
        )

        self.user_plan.stripe_customer_id = customer.id
        self.user_plan.save()
        return self.user_plan.stripe_customer_id

    def attach_payment_method(self, payment_method_id: str) -> None:
        customer_id = self.get_or_create_customer()
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

    def create_payment_intent(
        self, plan: Plan, payment_method_id: str
    ) -> stripe.PaymentIntent:
        price = Decimal(plan.price)
        amount = int(price * 100)

        self.attach_payment_method(payment_method_id)
        customer_id = self.user_plan.stripe_customer_id
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=plan.currency,
            customer=customer_id,
            payment_method=payment_method_id,
        )

    def create_subscription(
        self, plan: Plan, payment_method_id: str
    ) -> stripe.Subscription:
        self.attach_payment_method(payment_method_id)
        customer_id = self.user_plan.stripe_customer_id
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": plan.stripe_price_id}],
            default_payment_method=payment_method_id,
        )

    def process_payment(
        self, plan: Plan, payment_method_id: str, payment_type: str, **kwargs
    ):
        strategy = self._get_strategy(payment_type)
        return strategy.process(plan, payment_method_id, **kwargs)

    def _get_strategy(self, payment_type: str):
        strategies = {
            "card": CardPaymentStrategy(self),
            "blik": BlikPaymentStrategy(self),
        }
        return strategies.get(payment_type)

    def create_blik_payment_intent(
        self, plan: Plan, blik_code: str
    ) -> stripe.PaymentIntent:
        price = Decimal(plan.price)
        amount = int(price * 100)
        customer_id = self.get_or_create_customer()
        return stripe.PaymentIntent.create(
            amount=amount,
            currency="pln",
            customer=customer_id,
            payment_method_data={"type": "blik", "blik": {"code": blik_code}},
            payment_method_types=["blik"],
            confirm=True,
        )

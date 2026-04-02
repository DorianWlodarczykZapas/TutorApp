from decimal import Decimal

import stripe
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

    def create_payment_intent(self, plan: Plan) -> stripe.PaymentIntent:
        price = Decimal(plan.price)
        amount = int(price * 100)
        customer_id = self.get_or_create_customer()
        return stripe.PaymentIntent.create(
            amount=amount,
            currency=plan.currency,
            customer=customer_id,
        )

    def create_subscription(self, plan: Plan) -> stripe.Subscription:
        customer_id = self.get_or_create_customer()
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": plan.stripe_price_id}],
        )

    def process_payment(self, plan: Plan):
        if plan.type == Plan.PlanType.ULTIMATE:
            return self.create_payment_intent(plan)
        else:
            return self.create_subscription(plan)

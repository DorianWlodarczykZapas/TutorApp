import stripe
from django.core.management.base import BaseCommand
from plans.models import Plan
from plans.services import StripeService


class Command(BaseCommand):
    help = "Sync Stripe plans"

    def handle(self, *args, **options):
        StripeService()
        products = stripe.Product.list(active=True, expand=["data.default_price"])

        for product in products:
            plan_type = product.metadata["plan_type"]
            plan = Plan.objects.filter(type=plan_type).first()

            if plan:
                if product.default_price:
                    plan.stripe_price_id = product.default_price.id
                    plan.save()
                    self.stdout.write(self.style.SUCCESS(f"Synchronized: {plan.name}"))
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipped: {product.name} - no default_price"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f"Plan not found for type={plan_type}")
                )

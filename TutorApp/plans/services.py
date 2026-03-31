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

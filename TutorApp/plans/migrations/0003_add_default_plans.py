from django.db import migrations


def create_initial_plans(apps, schema_editor):
    Plan = apps.get_model("plans", "Plan")

    plans = [
        {
            "type": 1,
            "name": "Base",
            "description": "Basic free plan with limited features.",
            "price": 0.00,
            "billing_period": "Monthly",
            "advanced_features_enabled": False,
            "trial_days": 0,
        },
        {
            "type": 2,
            "name": "Premium",
            "description": "Full-featured plan with all access.",
            "price": 29.99,
            "billing_period": "Monthly",
            "advanced_features_enabled": True,
            "trial_days": 0,
        },
        {
            "type": 3,
            "name": "Trial",
            "description": "7-day free trial with limited access.",
            "price": 0.00,
            "billing_period": "7 days",
            "advanced_features_enabled": False,
            "trial_days": 7,
        },
    ]

    for plan_data in plans:
        if not Plan.objects.filter(type=plan_data["type"]).exists():
            Plan.objects.create(**plan_data)


class Migration(migrations.Migration):

    dependencies = [
        ("plans", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(create_initial_plans),
    ]

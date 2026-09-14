from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_alter_moderationaction_action"),
    ]

    operations = [
        migrations.AddField(
            model_name="channel",
            name="claimed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RemoveConstraint(
            model_name="follow",
            name="follow_has_one_valid_target",
        ),
        migrations.AddConstraint(
            model_name="follow",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("channel__isnull", False),
                        ("category__isnull", True),
                        ("institution__isnull", True),
                    ),
                    models.Q(
                        ("channel__isnull", True),
                        ("category__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="follow_has_one_valid_target",
            ),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_channel_claimed_at_and_follow_category_optional"),
    ]

    operations = [
        migrations.AddField(
            model_name="sponsoredlisting",
            name="sponsor_email",
            field=models.EmailField(default="", max_length=254),
            preserve_default=False,
        ),
    ]

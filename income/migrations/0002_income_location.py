from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("income", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="income",
            name="location",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=200,
                help_text="Location where income was earned (e.g., casino name)",
            ),
        ),
    ]

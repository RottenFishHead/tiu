from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0003_create_exploit_tables"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pokersession",
            name="hours",
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]

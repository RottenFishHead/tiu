from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0011_stopit_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="stopit",
            name="fails",
            field=models.IntegerField(
                choices=[(i, i) for i in range(51)],
                default=0,
            ),
        ),
    ]
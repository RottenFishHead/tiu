from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0004_alter_pokersession_hours"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pokersession",
            name="hours",
            field=models.DecimalField(blank=True, default=Decimal("0.00"), decimal_places=2, max_digits=6),
        ),
    ]
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_post_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="john",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="post",
            name="health",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="post",
            name="health_rating",
            field=models.DecimalField(
                decimal_places=1,
                max_digits=2,
                validators=[MinValueValidator(0.5), MaxValueValidator(5.0)],
                default=Decimal("3.0"),
            ),
            preserve_default=False,
        ),
    ]

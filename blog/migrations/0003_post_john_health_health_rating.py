from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_post_image"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "ALTER TABLE blog_post ADD COLUMN IF NOT EXISTS john text;",
                        "UPDATE blog_post SET john = '' WHERE john IS NULL;",
                        "ALTER TABLE blog_post ALTER COLUMN john SET NOT NULL;",
                    ],
                    reverse_sql="ALTER TABLE blog_post DROP COLUMN IF EXISTS john;",
                ),
                migrations.RunSQL(
                    sql=[
                        "ALTER TABLE blog_post ADD COLUMN IF NOT EXISTS health text;",
                        "UPDATE blog_post SET health = '' WHERE health IS NULL;",
                        "ALTER TABLE blog_post ALTER COLUMN health SET NOT NULL;",
                    ],
                    reverse_sql="ALTER TABLE blog_post DROP COLUMN IF EXISTS health;",
                ),
                migrations.RunSQL(
                    sql=[
                        "ALTER TABLE blog_post ADD COLUMN IF NOT EXISTS health_rating numeric(2,1);",
                        "UPDATE blog_post SET health_rating = 3.0 WHERE health_rating IS NULL;",
                        "ALTER TABLE blog_post ALTER COLUMN health_rating SET NOT NULL;",
                    ],
                    reverse_sql="ALTER TABLE blog_post DROP COLUMN IF EXISTS health_rating;",
                ),
            ],
            state_operations=[
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
            ],
        ),
    ]

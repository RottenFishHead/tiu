from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_post_john_health_health_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="status",
            field=models.CharField(
                choices=[("DF", "Draft"), ("PB", "Published")],
                default="PB",
                max_length=2,
            ),
        ),
    ]
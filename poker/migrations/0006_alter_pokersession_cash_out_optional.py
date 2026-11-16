from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0005_alter_pokersession_hours_optional"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pokersession",
            name="cash_out",
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
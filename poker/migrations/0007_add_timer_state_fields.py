from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0006_alter_pokersession_cash_out_optional"),
    ]

    operations = [
        migrations.AddField(
            model_name="pokersession",
            name="timer_status",
            field=models.CharField(choices=[("idle", "Idle"), ("running", "Running"), ("paused", "Paused"), ("completed", "Completed")], default="completed", max_length=20),
        ),
        migrations.AddField(
            model_name="pokersession",
            name="timer_started_at_ms",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="pokersession",
            name="timer_elapsed_ms",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="pokersession",
            name="timer_paused_ms",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="pokersession",
            name="timer_completed_at_ms",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]

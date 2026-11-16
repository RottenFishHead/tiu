from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0008_pokernotekeyword_pokernote"),
    ]

    operations = [
        migrations.CreateModel(
            name="StopIt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stop", models.CharField(max_length=250, unique=True)),
            ],
            options={
                "ordering": ["stop"],
            },
        ),
        migrations.AddField(
            model_name="pokersession",
            name="selected_stop",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sessions", to="poker.stopit"),
        ),
    ]

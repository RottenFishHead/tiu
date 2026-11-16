from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0007_add_timer_state_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PokerNoteKeyword",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="PokerNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, max_length=140)),
                ("note", models.TextField(max_length=5000)),
                ("is_important", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("keywords", models.ManyToManyField(blank=True, related_name="notes", to="poker.pokernotekeyword")),
                ("player", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="poker_notes", to=settings.AUTH_USER_MODEL)),
                ("session", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="poker_notes", to="poker.pokersession")),
            ],
            options={
                "ordering": ["-is_important", "-updated"],
                "indexes": [
                    models.Index(fields=["player", "-updated"], name="poker_poker_player__d8cb53_idx"),
                    models.Index(fields=["player", "is_important"], name="poker_poker_player__84b2af_idx"),
                ],
            },
        ),
    ]

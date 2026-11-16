from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_existing_records_to_first_user(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split('.')
    UserModel = apps.get_model(app_label, model_name)
    PlayerProfile = apps.get_model('poker', 'PlayerProfile')
    StopIt = apps.get_model('poker', 'StopIt')

    first_user = UserModel.objects.order_by('id').first()
    if not first_user:
        return

    PlayerProfile.objects.filter(owner__isnull=True).update(owner=first_user)
    StopIt.objects.filter(owner__isnull=True).update(owner=first_user)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('poker', '0013_stopit_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerprofile',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='poker_player_profiles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='stopit',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='poker_stop_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='stopit',
            name='stop',
            field=models.CharField(max_length=250),
        ),
        migrations.RunPython(assign_existing_records_to_first_user, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='stopit',
            constraint=models.UniqueConstraint(fields=('owner', 'stop'), name='uniq_stopit_owner_stop'),
        ),
    ]

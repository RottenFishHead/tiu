from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0014_playerprofile_owner_stopit_owner_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='stopit',
            name='uniq_stopit_owner_stop',
        ),
        migrations.RemoveField(
            model_name='playerprofile',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='stopit',
            name='owner',
        ),
        migrations.AlterField(
            model_name='stopit',
            name='stop',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]

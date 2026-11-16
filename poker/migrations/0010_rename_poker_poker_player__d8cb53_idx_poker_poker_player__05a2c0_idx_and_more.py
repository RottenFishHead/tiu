from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("poker", "0009_stopit_and_selected_stop"),
    ]

    operations = [
        # Intentionally left as a no-op.
        #
        # Some environments generated an index-rename migration here because
        # PokerNote index names were implicit in models.py. In databases where
        # those old index names do not exist, RenameIndex fails at migrate time.
        #
        # We pin explicit index names in models.py to the original names created
        # in 0008 and keep this migration as a stable placeholder so migration
        # history stays consistent across environments.
    ]

from django.db import migrations


def drop_legacy_columns(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("ALTER TABLE forum_post DROP COLUMN IF EXISTS embedding_status")
    schema_editor.execute("ALTER TABLE forum_post DROP COLUMN IF EXISTS embedding")


class Migration(migrations.Migration):
    dependencies = [("forum", "0002_post_vibe_post_vibe_status")]

    operations = [
        migrations.RunPython(drop_legacy_columns, migrations.RunPython.noop),
    ]

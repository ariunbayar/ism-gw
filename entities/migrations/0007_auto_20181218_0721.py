# Generated by Django 2.1.4 on 2018-12-17 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0006_auto_20181218_0655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='syncmodelcolumn',
            name='syncmodel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='columns', to='entities.SyncModel'),
        ),
    ]
# Generated by Django 2.1.4 on 2018-12-17 22:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0005_auto_20181218_0628'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SyncModelColumns',
            new_name='SyncModelColumn',
        ),
    ]
# Generated by Django 2.1.4 on 2018-12-23 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0024_auto_20181223_0859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ismpspalnm',
            name='change_id',
            field=models.BigIntegerField(db_index=True),
        ),
    ]
